import chess

# Piece values for evaluation
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

def evaluate_board(board):
    """
    Evaluate the board based on material count.
    Positive score favors white, negative favors black.
    """
    if board.is_checkmate():
        return -20000 if board.turn else 20000
    
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = PIECE_VALUES[piece.piece_type]
            score += value if piece.color == chess.WHITE else -value
    
    return score

def minimax(board, depth, alpha, beta, maximizing_player):
    """
    Minimax algorithm with alpha-beta pruning.
    
    Args:
        board: chess.Board object
        depth: remaining depth to search
        alpha: best value for maximizer
        beta: best value for minimizer
        maximizing_player: True if maximizing, False if minimizing
    
    Returns:
        Best evaluation score
    """
    # Base case: depth 0 or game over
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)
    
    if maximizing_player:
        max_eval = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # Beta cutoff
        return max_eval
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break  # Alpha cutoff
        return min_eval

def find_best_move(board, depth):
    """
    Find the best move for the current player.
    
    Args:
        board: chess.Board object
        depth: search depth
    
    Returns:
        Best move in UCI notation (e.g., 'e2e4')
    """
    best_move = None
    best_value = float('-inf') if board.turn == chess.WHITE else float('inf')
    alpha = float('-inf')
    beta = float('inf')
    
    for move in board.legal_moves:
        board.push(move)
        board_value = minimax(board, depth - 1, alpha, beta, 
                             not board.turn == chess.WHITE)
        board.pop()
        
        if board.turn == chess.WHITE:
            if board_value > best_value:
                best_value = board_value
                best_move = move
            alpha = max(alpha, best_value)
        else:
            if board_value < best_value:
                best_value = board_value
                best_move = move
            beta = min(beta, best_value)
    
    return best_move

if __name__ == "__main__":
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    
    board = chess.Board(fen)
    search_depth = 3 
    
    print(f"Position: {fen}")
    print(f"Current turn: {'White' if board.turn else 'Black'}")
    print(board)
    print()
    
    best_move = find_best_move(board, search_depth)
    
    if best_move:
        print(f"Best move (UCI): {best_move}")
        print(f"Best move (SAN): {board.san(best_move)}")
    else:
        print("No legal moves available")
