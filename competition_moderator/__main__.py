import subprocess
import time
import select
import sys
import os
import fcntl
import chess
from typing import Optional

class BotProcess:
    def __init__(self, module_path: str, color: str):
        self.path = module_path
        self.color = color

        # if not module_path.exists(): # This requires pathlib, commenting out
        #     raise FileNotFoundError(f"Bot module not found: {module_path}")
        
        print(f"Starting {color} bot: {module_path}")
        
        # --- FIX: Split the path to set PYTHONPATH and find the module name ---
        # User provides 'ai-chess-bot/demo-bot'
        # 1. The search path (to add to PYTHONPATH) is 'ai-chess-bot'
        # 2. The module name (to run with -m) is 'demo-bot'
        
        # os.path.normpath handles trailing slashes
        norm_path = os.path.normpath(module_path) 
        search_path = os.path.dirname(norm_path)
        module_name = os.path.basename(norm_path)

        # Ensure module names are valid Python identifiers (replace - with _)
        module_name = module_name.replace('-', '_')

        # Get the absolute path for the search directory
        abs_search_path = os.path.abspath(search_path)
        
        print(f"  - Module name: {module_name}")
        print(f"  - Adding to PYTHONPATH: {abs_search_path}")

        # Create a new environment for the subprocess
        # This inherits the current environment
        bot_env = os.environ.copy()
        
        # Prepend our new search path to the PYTHONPATH
        # This ensures our module is found first
        current_pythonpath = bot_env.get('PYTHONPATH', '')
        new_pythonpath = f"{abs_search_path}{os.pathsep}{current_pythonpath}"
        bot_env['PYTHONPATH'] = new_pythonpath
        
        self.process = subprocess.Popen(
            # Added '-u' for unbuffered I/O, which is crucial for subprocess comms
            ['python', '-u', '-m', module_name, 'play', color],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            env=bot_env # --- Pass the modified environment ---
        )

        # Set stderr to non-blocking so we can read from it without hanging
        try:
            fd = self.process.stderr.fileno()
            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        except Exception as e:
            print(f"Warning: Could not set stderr to non-blocking (OS may not support fcntl): {e}")


        self.time_remaining = 300.0  # 5 minutes in seconds
    
    def send_move(self, move: str):
        """Sends a move to the bot's stdin."""
        try:
            # Check if the process is still alive before writing
            if self.process.poll() is not None:
                print(f"Bot {self.color} is dead. Cannot send move.")
                return

            self.process.stdin.write(move + '\n')
            self.process.stdin.flush()
        
        # --- FIX 1: Correctly catch the exception ---
        except (BrokenPipeError, OSError) as e:
            # This happens if the bot died between the poll() check and the write()
            print(f"Bot {self.color} error on send (BrokenPipe): {e}. Bot has likely crashed.")
            self.read_stderr() # Print any last words from the bot

    def read_stderr(self) -> str:
        """Reads from stderr without blocking."""
        try:
            return self.process.stderr.read()
        except (IOError, TypeError): # Handle no output
            return ""

    def get_move(self, timeout) -> Optional[str]:
        """
        Gets a move from the bot's stdout.
        Returns the move string, or None if the bot timed out, crashed, or sent EOF.
        """
        ready, _, _ = select.select([self.process.stdout], [], [], timeout)

        if ready:
            line = self.process.stdout.readline()
            
            # --- FIX 2: Check for EOF (empty string) ---
            if not line: 
                # An empty string from readline() means EOF - the process died.
                stderr_output = self.read_stderr()
                print(f"Bot {self.color} process died (EOF). Stderr:\n---\n{stderr_output}\n---")
                return None # Signal death/crash
                
            return line.strip()
        
        # Timeout occurred
        stderr_output = self.read_stderr()
        print(f"Bot {self.color} timed out. Stderr so far:\n---\n{stderr_output}\n---")
        return None

    def close(self):
        """Terminate the bot process."""
        print(f"Stopping {self.color} bot...")
        if self.process.poll() is None: # Only terminate if it's running
            try:
                self.process.terminate()
                self.process.wait(timeout=2) # Give it 2s to shut down gracefully
            except Exception:
                self.process.kill() # Force kill if terminate fails
        
        print(f"{self.color} bot stopped.")

White_bot = BotProcess(sys.argv[1], "w")
Black_bot = BotProcess(sys.argv[2], "b")

fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
board = chess.Board(fen)

print(board)
while True:
    # White's turn
    move = White_bot.get_move(300)
    try:
        parsed_move = board.parse_san(move)
        if board.is_legal(parsed_move):
            board.push(parsed_move)
            print(f"White makes move: {move}")
            print(board)
            Black_bot.send_move(move)
        else:
            print(f"Illegal move by White: {move}")
            break
    except Exception as e:
        print(f"Invalid move format by White: {move} - {e}")
        break

    # Black's turn
    move = Black_bot.get_move(300)
    try:
        parsed_move = board.parse_san(move)
        if board.is_legal(parsed_move):
            board.push(parsed_move)
            print(f"Black makes move: {move}")
            print(board)
            White_bot.send_move(move)
        else:
            print(f"Illegal move by Black: {move}")
            break
    except Exception as e:
        print(f"Invalid move format by Black: {move} - {e}")
        break