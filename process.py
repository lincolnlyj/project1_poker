from poker import PokerPlayer, Poker


class Process:
    """
    用于将poker.py的算法和界面做联系
    """

    def __init__(self):
        self.__reset()

    def __reset(self):
        self.problem = PokerPlayer()
        self.player1 = PokerPlayer()
        self.player2 = PokerPlayer()

    def random_deal(self, pokerCnt):
        self.__reset()
        self.problem.deal_random(pokerCnt)
        return self.problem.get_init_order()

    def specified_deal(self, pokerOrderLst):
        self.__reset()
        pokerLst = []
        for order in pokerOrderLst:
            pokerLst.append((Poker(order).num, Poker(order).suit))
        self.problem.deal_specified(pokerLst)

    def solve_without_score(self):
        self.problem.solve_without_score()
        path = []
        for action in self.problem.path:
            actionOrder = []
            try:
                for item in action:
                    actionOrder.append(Poker.get_order(item))
            except TypeError:
                actionOrder.append(Poker.get_order(action))
            path.append(actionOrder)
        return self.problem.step, path

    def solve_with_score(self):
        self.problem.solve_with_score(self.problem.initNode, 0, 0)
        path = []
        for action in self.problem.path:
            actionOrder = []
            try:
                for item in action:
                    actionOrder.append(Poker.get_order(item))
            except TypeError:
                actionOrder.append(Poker.get_order(action))
            path.append(actionOrder)
        return self.problem.score, self.problem.step, path

    def deal_player1(self, pokerCnt):
        self.player1 = PokerPlayer()
        self.player1.deal_random(pokerCnt)
        return self.player1.get_init_order()

    def deal_player2(self, pokerCnt):
        self.player2 = PokerPlayer()
        self.player2.deal_random(pokerCnt)
        return self.player2.get_init_order()

    def gaming(self):
        action = None
        player1ActionLst = []
        player2ActionLst = []
        winner = 0
        while self.player1.curNode and self.player2.curNode:
            action = self.player1.gaming(action)
            actionLst = []
            if action:
                try:
                    for item in action[1]:
                        actionLst.append(Poker.get_order(item))
                except TypeError:
                    actionLst.append(Poker.get_order(action[1]))
            player1ActionLst.append(actionLst)
            if len(self.player1.curNode.state) == 0:
                winner = 1
                break
            action = self.player2.gaming(action)
            actionLst = []
            if action:
                try:
                    for item in action[1]:
                        actionLst.append(Poker.get_order(item))
                except TypeError:
                    actionLst.append(Poker.get_order(action[1]))
            player2ActionLst.append(actionLst)
            if len(self.player2.curNode.state) == 0:
                winner = 2
                break

        return player1ActionLst, player2ActionLst, winner
