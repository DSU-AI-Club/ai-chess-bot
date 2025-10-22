import subprocess
import json
import time
import chess
import sys
from pathlib import Path

class BotProcess:
    def __init__(self, module_name):
        self.module_name = module_name
        module_path = Path(__file__).parent.parent / f"{module_name}"
        
        if not module_path.exists():
            raise FileNotFoundError(f"Bot module not found: {module_path}")
        
        self.process = subprocess.Popen(
            ['python', '-m', str(module_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line buffered
        )
        self.time_remaining = 300.0  # 5 minutes in seconds
    
    def get_move(self, gamestate, timeout=None):
        """Send gamestate to bot and get move back with timing"""
        if timeout is None:
            timeout = self.time_remaining
        
        start_time = time.time()
        
        try:
            # Send gamestate as JSON line
            self.process.stdin.write(json.dumps(gamestate) + '\n')
            self.process.stdin.flush()
            
            # Read move from stdout with timeout
            self.process.stdout.flush()
            move_line = self._read_with_timeout(timeout)
            
            elapsed = time.time() - start_time
            self.time_remaining -= elapsed
            
            if self.time_remaining <= 0:
                return None, "timeout"
            
            if move_line is None:
                return None, "timeout"
            
            move_data = json.loads(move_line)
            return move_data.get('move'), None
            
        except json.JSONDecodeError as e:
            return None, f"invalid_json: {e}"
        except Exception as e:
            return None, f"error: {e}"
    
    def _read_with_timeout(self, timeout):
        """Read a line from stdout with timeout"""
        import select
        
        # Use select to wait for data with timeout
        ready, _, _ = select.select([self.process.stdout], [], [], timeout)
        
        if ready:
            return self.process.stdout.readline().strip()
        return None
    
    def close(self):
        """Terminate the bot process"""
        try:
            self.process.terminate()
            self.process.wait(timeout=2)
        except:
            self.process.kill()

class ChessModerator:
    def __init__(self, white_module, black_module):
        self.board = chess.Board()
        self.white_bot = BotProcess(white_module)
        self.black_bot = BotProcess(black_module)
        self.white_name = white_module
        self.black_name = black_module
    
    def run_game(self):
        """Run a complete chess game and return the winner"""
        print(f"Starting game: {self.white_name} (White) vs {self.black_name} (Black)")
        print(f"Initial position:\n{self.board}\n")
        
        move_count = 0
        
        try:
            while not self.board.is_game_over():
                current_bot = self.white_bot if self.board.turn == chess.WHITE else self.black_bot
                current_name = self.white_name if self.board.turn == chess.WHITE else self.black_name
                color = "White" if self.board.turn == chess.WHITE else "Black"
                
                # Prepare gamestate
                gamestate = {
                    'fen': self.board.fen(),
                    'legal_moves': [move.uci() for move in self.board.legal_moves],
                    'color': 'white' if self.board.turn == chess.WHITE else 'black',
                    'move_number': self.board.fullmove_number,
                    'time_remaining': current_bot.time_remaining
                }
                
                print(f"Move {self.board.fullmove_number} - {color} ({current_name}) to move")
                print(f"Time remaining: {current_bot.time_remaining:.1f}s")
                
                # Get move from bot
                move_uci, error = current_bot.get_move(gamestate)
                
                if error:
                    print(f"\n{color} ({current_name}) error: {error}")
                    winner = self.black_name if self.board.turn == chess.WHITE else self.white_name
                    reason = error
                    return winner, reason
                
                # Validate and apply move
                try:
                    move = chess.Move.from_uci(move_uci)
                    if move not in self.board.legal_moves:
                        print(f"\n{color} ({current_name}) proposed illegal move: {move_uci}")
                        winner = self.black_name if self.board.turn == chess.WHITE else self.white_name
                        return winner, "illegal_move"
                    
                    self.board.push(move)
                    print(f"{color} plays: {move_uci}")
                    print(f"Position:\n{self.board}\n")
                    
                except ValueError:
                    print(f"\n{color} ({current_name}) proposed invalid move format: {move_uci}")
                    winner = self.black_name if self.board.turn == chess.WHITE else self.white_name
                    return winner, "invalid_move_format"
            
            # Game ended normally
            result = self.board.result()
            print(f"\nGame over: {result}")
            
            if result == "1-0":
                return self.white_name, "checkmate"
            elif result == "0-1":
                return self.black_name, "checkmate"
            else:
                return None, f"draw ({self.board.outcome().termination.name})"
        
        finally:
            self.white_bot.close()
            self.black_bot.close()

def main():
    if len(sys.argv) != 3:
        print("Usage: python __main__.py <white_bot_module> <black_bot_module>")
        print("Example: python __main__.py bot_alpha bot_beta")
        sys.exit(1)
    
    white_module = sys.argv[1]
    black_module = sys.argv[2]
    
    moderator = ChessModerator(white_module, black_module)
    winner, reason = moderator.run_game()
    
    if winner:
        print(f"\n{'='*50}")
        print(f"WINNER: {winner}")
        print(f"Reason: {reason}")
        print(f"{'='*50}")
    else:
        print(f"\n{'='*50}")
        print(f"DRAW")
        print(f"Reason: {reason}")
        print(f"{'='*50}")

if __name__ == "__main__":
    main()