import subprocess
import json
import time
import chess
import sys
from pathlib import Path

class BotProcess:
    def __init__(self, module_name, color):
        self.module_name = module_name
        module_path = Path(__file__).parent.parent / f"{module_name}"
        
        if not module_path.exists():
            raise FileNotFoundError(f"Bot module not found: {module_path}")
        
        self.process = subprocess.Popen(
            ['python', '-m', str(module_path), color],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line buffered
        )
        self.time_remaining = 300.0  # 5 minutes in seconds
    
    def get_move(self, last_move_san, timeout=None):
        """Send opponent's last move to bot and get move back with timing"""
        if timeout is None:
            timeout = self.time_remaining
        
        start_time = time.time()
        
        try:
            # Send opponent's last move as plain text (or empty line for first move)
            move_to_send = last_move_san if last_move_san else ""
            self.process.stdin.write(move_to_send + '\n')
            self.process.stdin.flush()
            
            # Read move from stdout with timeout
            self.process.stdout.flush()
            move_san = self._read_with_timeout(timeout)
            
            elapsed = time.time() - start_time
            self.time_remaining -= elapsed
            
            if self.time_remaining <= 0:
                return None, "timeout"
            
            if move_san is None:
                return None, "timeout"
            
            return move_san, None
        
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
        self.white_bot = BotProcess(white_module, 'w')
        self.black_bot = BotProcess(black_module, 'b')
        self.white_name = white_module
        self.black_name = black_module
        self.last_move_san = None
    
    def run_game(self):
        """Run a complete chess game and return the winner"""
        print(f"Starting game: {self.white_name} (White) vs {self.black_name} (Black)")
        print(f"Initial position:\n{self.board}\n")
        
        try:
            while not self.board.is_game_over():
                current_bot = self.white_bot if self.board.turn == chess.WHITE else self.black_bot
                current_name = self.white_name if self.board.turn == chess.WHITE else self.black_name
                color = "White" if self.board.turn == chess.WHITE else "Black"
                
                print(f"Move {self.board.fullmove_number} - {color} ({current_name}) to move")
                print(f"Time remaining: {current_bot.time_remaining:.1f}s")
                
                # Get move from bot
                move_san, error = current_bot.get_move(self.last_move_san)
                
                if error:
                    print(f"\n{color} ({current_name}) error: {error}")
                    winner = self.black_name if self.board.turn == chess.WHITE else self.white_name
                    reason = error
                    return winner, reason
                
                # Validate and apply move
                try:
                    move = self.board.parse_san(move_san)
                    self.board.push(move)
                    self.last_move_san = move_san
                    self.move_history.append({
                        'san': move_san,
                        'color': color,
                        'player': current_name,
                        'fen': self.board.fen()
                    })
                    
                    print(f"{color} plays: {move_san}")
                    print(f"Position:\n{self.board}\n")
                    
                except (ValueError, chess.IllegalMoveError, chess.InvalidMoveError) as e:
                    print(f"\n{color} ({current_name}) proposed invalid/illegal move: {move_san}")
                    winner = self.black_name if self.board.turn == chess.WHITE else self.white_name
                    return winner, "illegal_move"
            
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