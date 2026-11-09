# game-AI/dfpn.py

import time
from copy import deepcopy
from util import get_legal_moves, apply_move, is_terminal, opponent, count_discs

# ========================================
# 探索の制限（どちらかに達したら探索を打ち切る）
# ========================================
DFPN_TIME_LIMIT = 10.0   # 秒。メモリ使用量の増加を抑える目的もある
DFPN_MAX_STEPS = 150_000

class Node:
    """
    df-pn探索の論理ノード。
    - is_or_node: TrueならORノード（先手番の選択）、FalseならANDノード（相手手番の反証ノード）
    - proof, disproof: 証明数／反証数
    - children: 展開後の子ノードリスト
    - expanded: 一度展開したかどうか
    """
    def __init__(self, board, player, is_or_node, move=None):
        self.board = board
        self.player = player
        self.is_or_node = is_or_node
        self.move = move
        self.proof = 1
        self.disproof = 1
        self.children = []
        self.expanded = False

def initialize_proof_disproof(node):
    """
    与えられたノードが終局かどうかを調べ、探索の根（AI側）から見た結果で値を設定する。
    - AIの勝ち確定: proof=0, disproof=INF
    - AIの負け確定: proof=INF, disproof=0
    - 引き分け: proof=INF, disproof=INF
    - 非終局: proof=1, disproof=1

    ORノードの手番は常にAI、ANDノードの手番は常に相手なので、
    ノードの手番(node.player)からAI側の色を求めて石数を比べる。
    """
    INF = float('inf')

    if is_terminal(node.board):
        ai_player = node.player if node.is_or_node else opponent(node.player)
        ai_discs = count_discs(node.board, ai_player)
        opp_discs = count_discs(node.board, opponent(ai_player))
        if ai_discs > opp_discs:
            node.proof = 0
            node.disproof = INF
        elif ai_discs < opp_discs:
            node.proof = INF
            node.disproof = 0
        else:
            node.proof = INF
            node.disproof = INF
    else:
        node.proof = 1
        node.disproof = 1

    return node

def expand_node(node):
    if node.expanded:
        return

    legal_moves = get_legal_moves(node.board, node.player)

    if not legal_moves:
        # パスの場合は、相手手番にして子ノードを1つだけ作成
        new_board = deepcopy(node.board)
        child_node = Node(
            board=new_board,
            player=opponent(node.player),
            is_or_node=not node.is_or_node,
            move=None
        )
        initialize_proof_disproof(child_node)
        node.children.append(child_node)
    else:
        for move in legal_moves:
            new_board = apply_move(deepcopy(node.board), move, node.player)
            child_node = Node(
                board=new_board,
                player=opponent(node.player),
                is_or_node=not node.is_or_node,
                move=move
            )
            initialize_proof_disproof(child_node)
            node.children.append(child_node)

    node.expanded = True

def select_child(node):
    """
    ORノードなら proof number が最小の子ノードを、
    ANDノードなら disproof number が最小の子ノードを返す。
    """
    if not node.children:
        return None

    if node.is_or_node:
        # ORノード：proof が最小の子を選ぶ
        return min(node.children, key=lambda child: child.proof)
    else:
        # ANDノード：disproof が最小の子を選ぶ
        return min(node.children, key=lambda child: child.disproof)

def update_proof_disproof_numbers(node):
    """
    子ノードの proof / disproof を使って、このノードの値を更新する。
    """
    if not node.children:
        return

    if node.is_or_node:
        node.proof = min(child.proof for child in node.children)
        node.disproof = sum(child.disproof for child in node.children)
    else:
        node.proof = sum(child.proof for child in node.children)
        node.disproof = min(child.disproof for child in node.children)

def dfpn_search(board, player):
    """
    df-pn探索のメイン関数。
    残り手数が12以下で呼ばれる前提。
    ステップ上限・時間制限以内で証明／反証を進め、勝ち筋の手を返す。

    勝ち筋の手を返せなかった場合（時間切れ・ステップ上限・勝てない局面）は None を返す。
    その場合の手の決定は、呼び出し側（ai_player.decide_move）が alpha_beta_search で行う。
    """

    MAX_STEPS = DFPN_MAX_STEPS
    start_time = time.monotonic()
    steps = 0

    root = Node(board, player, is_or_node=True)
    initialize_proof_disproof(root)

    if root.proof == 0:
        return None  # すでに勝ち確定

    while (root.proof != 0 and root.disproof != 0
           and steps < MAX_STEPS
           and time.monotonic() - start_time < DFPN_TIME_LIMIT):
        current = root
        path = [current]

        # 探索パスを一つ辿る（select → expand）
        while current.expanded and current.children:
            current = select_child(current)
            path.append(current)

        expand_node(current)
        steps += 1

        # proof/disproof の更新
        for node in reversed(path):
            if not node.children:
                continue
            if node.is_or_node:
                node.proof = min(child.proof for child in node.children)
                node.disproof = sum(child.disproof for child in node.children)
            else:
                node.proof = sum(child.proof for child in node.children)
                node.disproof = min(child.disproof for child in node.children)

    # root の子ノードのうち、proof = 0 を達成した手を返す
    for child in root.children:    
        if child.proof == 0 and child.move is not None:
            return child.move  # 勝ち筋の手
    return None      # 勝ちが見つからなかった場合（時間切れ・引き分け・負け）
