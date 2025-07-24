# game-AI/ai_player.py

from search import alpha_beta_search
from dfpn import dfpn_search

def count_empty_cells(board):
    return sum(cell == 0 for layer in board for row in layer for cell in row)

def decide_move(board, player):
    empty_cells = count_empty_cells(board)
    print('[AI] 空きマス数:', empty_cells)
    print('[AI] プレイヤー:', player)

    if empty_cells <= 12:
        print('[AI] dfpn_search に入ります')
        move = dfpn_search(board, player)
    else:
        print('[AI] alpha_beta_search に入ります')
        move = alpha_beta_search(board, player)

    print('[AI] 選ばれた手:', move)
    return move
