# game-AI/search.py

from evaluation import evaluate_board
from util import get_legal_moves, is_terminal, apply_move

MAX_DEPTH = 3  # 現在の設計における読みの深さ

def alpha_beta_search(board, player, depth=MAX_DEPTH):
    player_val = 1 if player == 'black' else -1
    def max_value(board, alpha, beta, depth):
        if depth == 0 or is_terminal(board):
            return evaluate_board(board, player), None
        max_eval = float('-inf')
        best_move = None
        for move in get_legal_moves(board, player):
            new_board = apply_move(board, move, player)
            eval, _ = min_value(new_board, alpha, beta, depth - 1)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            if max_eval >= beta:
                return max_eval, best_move
            alpha = max(alpha, max_eval)
        return max_eval, best_move

    def min_value(board, alpha, beta, depth):
        opponent = -player  # ← ★ここを必ずインデント
        if depth == 0 or is_terminal(board):
            return evaluate_board(board, player), None
        min_eval = float('inf')
        best_move = None
        for move in get_legal_moves(board, opponent):
            new_board = apply_move(board, move, opponent)
            eval, _ = max_value(new_board, alpha, beta, depth - 1)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            if min_eval <= alpha:
                return min_eval, best_move
            beta = min(beta, min_eval)
        return min_eval, best_move

    return max_value(board, float('-inf'), float('inf'), depth)[1]