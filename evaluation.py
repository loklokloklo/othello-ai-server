# game-AI/evaluation.py

from itertools import product
from util import is_on_board, get_legal_moves, DIRECTIONS
import math

# 評価の重み（グローバル）
WEIGHTS = {
    "corner": 1000,
    "stable": 100,
    "opp_mobility": -5,
    "opp_stable": -40,
    "frontier_log_coeff": 5,  # フロンティア石ペナルティの係数a
}

#角のリスト
CORNERS = [(x, y, z) for x in [0, 3] for y in [0, 3] for z in [0, 3]]

def get_stable_discs(board, player):
    size = 4
    stable = set()

    def is_player_disc(x, y, z):
        return is_on_board(x, y, z) and board[x][y][z] == player
    
    # 初期候補: 4連続や辺埋まり（基本ライン）
    for dx, dy, dz in DIRECTIONS:
        for x in range(size):
            for y in range(size):
                for z in range(size):
                    line = [(x + i * dx, y + i * dy, z + i * dz) for i in range(4)]
                    if all(is_on_board(xi, yi, zi) and board[xi][yi][zi] == player for xi, yi, zi in line):
                        stable.update(line)

    # 角隣接の辺処理・囲まれ型追加
    for corner in CORNERS:
        cx, cy, cz = corner
        if board[cx][cy][cz] != player:
            continue
        for dx, dy, dz in DIRECTIONS:
            x, y, z = cx + dx, cy + dy, cz + dz
            line = []
            while is_player_disc(x, y, z):
                line.append((x, y, z))
                x += dx
                y += dy
                z += dz
            if line:
                stable.update(line)

     # 拡張安定判定：確定石や盤外に囲まれ、相手に裏返されない
    changed = True
    while changed:
        changed = False
        for x in range(size):
            for y in range(size):
                for z in range(size):
                    if (x, y, z) in stable or board[x][y][z] != player:
                        continue
                    safe = True
                    for dx, dy, dz in DIRECTIONS:
                        nx, ny, nz = x + dx, y + dy, z + dz
                        while is_on_board(nx, ny, nz):
                            stone = board[nx][ny][nz]
                            if stone == 'empty':
                                safe = False
                                break
                            if stone != player and (nx, ny, nz) not in stable:
                                safe = False
                                break
                            if stone == player:
                                break
                            nx += dx
                            ny += dy
                            nz += dz
                        if not safe:
                            break
                    if safe:
                        stable.add((x, y, z))
                        changed = True
    
    # 角を除外
    stable -= set(CORNERS)
    return stable

def calculate_frontier_penalty(empty_neighbors, a):
    """
    フロンティア石のペナルティを計算する関数
    P(x) = 0 (x = 0 or 1)
    P(x) = -a * log(x) (x > 1)
    """
    if empty_neighbors <= 1:
        return 0
    else:
        penalty = -a * math.log(empty_neighbors)
        return round(penalty)  # 四捨五入して整数に

# 評価関数に確定石を加点
def evaluate_board(board, current_player):
    score = 0
    opponent = -current_player  # ← 修正！

     # 自分の角の評価
    for x, y, z in CORNERS:
        if board[x][y][z] == current_player:
            score += WEIGHTS["corner"]

    # 自分の確定石の加点
    stable = get_stable_discs(board, current_player)
    score += WEIGHTS["stable"] * len(stable)

    # 相手の確定石の減点
    opp_stable = get_stable_discs(board, opponent)
    score += WEIGHTS["opp_stable"] * len(opp_stable)

    # 自分のフロンティア石の評価（マス種別ごとに方向を制限し、新しいペナルティ関数を使用）
    a = WEIGHTS["frontier_log_coeff"]
    for x in range(4):
        for y in range(4):
            for z in range(4):
                if board[x][y][z] != current_player:
                    continue
                # 角はフロンティア石に含めない
                if (x, y, z) in CORNERS:
                    continue

                # 石が置かれているのでフロンティア石対象外
                # （ここで current_player の石のマスのみを処理しているためOK）

                # まずマスのタイプ判定
                extremes = [coord in (0, 3) for coord in (x, y, z)]
                num_extremes = sum(extremes)

                # 1: 辺上マス（2つの座標が端で1つが内側）
                if num_extremes == 2:
                    # 辺の方向ベクトルを取る：端でない座標軸方向のみ
                    dir_axes = []
                    if not extremes[0]:  # x が内側 → x軸方向を数える
                        dir_axes.append((1, 0, 0))
                        dir_axes.append((-1, 0, 0))
                    if not extremes[1]:  # y が内側
                        dir_axes.append((0, 1, 0))
                        dir_axes.append((0, -1, 0))
                    if not extremes[2]:  # z が内側
                        dir_axes.append((0, 0, 1))
                        dir_axes.append((0, 0, -1))

                # 2: 面上マス（1つの座標が端で2つが内側）
                elif num_extremes == 1:
                    dir_axes = []
                    # 端でない2軸方向を両方数える
                    if not extremes[0]:  # x軸方向
                        dir_axes += [(1, 0, 0), (-1, 0, 0)]
                    if not extremes[1]:
                        dir_axes += [(0, 1, 0), (0, -1, 0)]
                    if not extremes[2]:
                        dir_axes += [(0, 0, 1), (0, 0, -1)]

                # 3: 内部マス（0 or 3 の座標が1つもない）→ フロンティア対象外
                else:
                    continue

                # 選出した方向だけで隣接空きマスをカウント
                empty_neighbors = 0
                for dx, dy, dz in dir_axes:
                    nx, ny, nz = x + dx, y + dy, z + dz
                    if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4:
                        if board[nx][ny][nz] == 'empty':
                            empty_neighbors += 1

                # 新しいペナルティ関数を使用
                penalty = calculate_frontier_penalty(empty_neighbors, a)
                score += penalty

# 相手の合法手数（opp_mobility）
    opponent_moves = get_legal_moves(board, opponent)
    mobility_score = len(opponent_moves)
    score += WEIGHTS["opp_mobility"] * mobility_score

    return score