# ただのAKQゲーム。拡張性を重視して複雑にしている部分もある
# TODO: アクションをクラス化、アクションにbet額などを紐づけして深スタック対応
CHECK = "check"
CALL = "call"
BET = "bet"
FOLD = "fold"


class Game:
    def __init__(self, stack: list):
        # マルチにする場合、stackから人数を決定し、nodeの作成などに使用
        self.FIRST_STACK = stack.copy()
        self.root = GameNode(stack=stack.copy(), game=self)
        self.nodes = {self.root}


class GameNode:
    """何のハンド持ってるか区別しないゲームの状態(情報集合)"""

    def __init__(self, player=0, pot=1, history=None, stack=None, game=None):
        self.history = history if history is not None else []  # 公開情報の履歴。偶然手番を含まない
        self.player = player
        self.pot = pot
        self.child = {}  # 子ノードへの辞書。キーはアクション
        self.stack = stack if stack is not None else []
        self.game = game

    def make_child(self, action: str):
        child = GameNode(
                player=1 - self.player,  # プレイヤーは交互
                pot=self.pot,
                history=self.history + [action],
                stack=self.stack.copy(),
                # Gameのnodesにchildを追加するときなどのため、
                # 何のGameクラスのノードなのかをノードに記憶させる。もっといい方法があるか？
                game=self.game
        )
        self.child[action] = child

        if action in {CALL, BET}:
            # TODO:深いスタックに対応
            child.pot += 1
            child.stack[self.player] -= 1

        self.game.nodes.add(child)
        return child

    def payoff(self, ip_hand: chr, player: int):
        # A,Q側ハンドからプレイヤーの利得を求める

        if not self.is_terminal():
            raise ValueError("payoff() is for only terminal node!")

        if self.history[-1] == FOLD:
            # フォールドが最後の場合、手番のプレイヤーが勝ち
            win = self.player == player
        else:
            # フォールドが最後でない場合、ハンドが強いプレイヤーが勝ち
            if ip_hand == "q" and player == 0:
                win = True
            elif ip_hand == "a" and player == 1:
                win = True
            else:
                win = False

        if win:
            return self.pot + self.stack[player] - self.game.FIRST_STACK[player]
        else:
            return self.stack[player] - self.game.FIRST_STACK[player]

    def is_terminal(self):
        # 子ノードがなかったら終端ノードとみなす
        return len(self.child) == 0

    def display(self):
        player = "None" if self.is_terminal() else self.player
        print(f"Player: {player}, History: {self.history}, Pot: {self.pot}, Stack: {self.stack}")


class CFR():
    def __init__(self, game: Game):
        self.game = game

        # counter factual regretの総和。regret_sum[node][hand][action]
        self.regret_sum = {}
        for node in game.nodes:
            if node.is_terminal():
                continue
            actions = node.child
            hands = ["a", "q"] if node.player == 1 else ["k"]
            self.regret_sum[node] = {hand: {action: 0 for action in actions} for hand in hands}

    def cal_CFR(self):
        for t in range(1):
            strategy = self.cal_strategy()
            print(strategy)
            # cf value計算
            # strategyからcf 到達確率を計算
            # strategyからcf valueを計算
            # cf

    def cal_strategy(self):
        # regret_sumから今回の戦略を算出する
        # return: strategy[node][action][hand]

        strategy = {}
        for node in self.game.nodes:
            if node.is_terminal():
                continue
            strategy[node] = {}

            for hand in self.regret_sum[node]:
                strategy[node][hand] = {}
                infoset_total_regret = sum(self.regret_sum[node][hand].values())

                # 情報集合内の全てのregretを足しても正にならない場合、等確立にする
                for action in node.child:
                    if infoset_total_regret > 0:
                        strategy[node][hand][action] = self.regret_sum[node][hand][action] / infoset_total_regret
                    else:
                        strategy[node][hand][action] = 1 / len(node.child)
        return strategy


# akqゲームを構築
# アクションの順番でノードを作る。eg: root->check->bet->callであれば、ブラフキャッチ
akq = Game([1, 1])
node_b = akq.root.make_child(BET)
node_b.make_child(CALL)
node_b.make_child(FOLD)
node_c = akq.root.make_child(CHECK)
node_c.make_child(CHECK)
node_c_b = node_c.make_child(BET)
node_c_b.make_child(CALL)
node_c_b.make_child(FOLD)


# 適当にいじろう！
for node in akq.nodes:
    node.display()

test = CFR(akq)
test.cal_CFR()
