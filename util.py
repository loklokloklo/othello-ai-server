# game-AI/util.py

DIRECTIONS = [
    (1, 0, 0), (-1, 0, 0),
    (0, 1, 0), (0, -1, 0),
    (0, 0, 1), (0, 0, -1),
    (1, 1, 0), (-1, -1, 0),
    (1, -1, 0), (-1, 1, 0),
    (1, 0, 1), (-1, 0, -1),
    (1, 0, -1), (-1, 0, 1),
    (0, 1, 1), (0, -1, -1),
    (0, 1, -1), (0, -1, 1),
    (1, 1, 1), (-1, -1, -1),
    (1, -1, 1), (-1, 1, -1),
    (1, 1, -1), (-1, -1, 1),
    (1, -1, -1), (-1, 1, 1)
]

def opponent(player):
    return -player

def count_discs(board, player):
    return sum(cell == player for layer in board for row in layer for cell in row)


def is_on_board(x, y, z):
    return 0 <= x < 4 and 0 <= y < 4 and 0 <= z < 4

def is_legal_move(board, x, y, z, player):
    if not is_on_board(x, y, z) or board[x][y][z] != 0:
        return False

    opponent = -player
    for dx, dy, dz in DIRECTIONS:
        nx, ny, nz = x + dx, y + dy, z + dz
        found_opponent = False

        while is_on_board(nx, ny, nz) and board[nx][ny][nz] == opponent:
            found_opponent = True
            nx += dx
            ny += dy
            nz += dz

        if found_opponent and is_on_board(nx, ny, nz) and board[nx][ny][nz] == player:
            return True

    return False

def get_legal_moves(board, player):
    legal_moves = []
    for x in range(4):
        for y in range(4):
            for z in range(4):
                if is_legal_move(board, x, y, z, player):
                    legal_moves.append((x, y, z))
    return legal_moves

import copy

def apply_move(board, move, player):
    x, y, z = move
    new_board = copy.deepcopy(board)
    new_board[x][y][z] = player

    opponent = -player
    for dx, dy, dz in DIRECTIONS:
        nx, ny, nz = x + dx, y + dy, z + dz
        flipped = []

        while is_on_board(nx, ny, nz) and new_board[nx][ny][nz] == opponent:
            flipped.append((nx, ny, nz))
            nx += dx
            ny += dy
            nz += dz

        if is_on_board(nx, ny, nz) and new_board[nx][ny][nz] == player:
            for fx, fy, fz in flipped:
                new_board[fx][fy][fz] = player

    return new_board

def is_terminal(board):
    return len(get_legal_moves(board, 1)) == 0 and len(get_legal_moves(board, -1)) == 0
