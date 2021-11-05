import random
from math import ceil, log
import sortedcontainers
from collections import OrderedDict


class PriorityQueue(object):
    """
    优先级队列
    """
    def __init__(self, node, key=None):
        self._queue = sortedcontainers.SortedList([node], key)
        self._count = 0

    def push(self, node):
        self._queue.add(node)

    def pop(self):
        return self._queue.pop(index=0)

    def empty(self):
        return len(self._queue) == 0

    def compare_and_replace(self, i, node):
        if node < self._queue[i]:
            self._queue.pop(index=i)
            self._queue.add(node)

    def find(self, node):
        try:
            loc = self._queue.index(node)
            return loc
        except ValueError:
            return None

    def __iter__(self):
        return self

    def __next__(self):
        if self._count < len(self._queue):
            result = self._queue[self._count]
            self._count += 1
            return result
        else:
            raise StopIteration

    def __getitem__(self, idx):
        return self._queue[idx] if not self.empty() else None

    def __len__(self):
        return len(self._queue)


class Poker:
    """
    扑克牌类，用于存储比较扑克牌
    大小王均为JOKER，利用花色进行区分，小王为红桃，大王为黑桃
    比较大小和相等关系时不考虑牌的类型
    """
    __pokerMap = {'3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
                  '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14, '2': 15,
                  'JOKER': 16}# 扑克牌映射
    __rePokerMap = {3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9',
                    10: '10', 11: 'J', 12: 'Q', 13: 'K', 14: 'A', 15: '2',
                    16: 'JOKER'}# 反向扑克牌映射
    __suitType = ['heart', 'spade', 'club', 'diamond']

    def __init__(self, *args):
        if len(args) == 2:
            self.__init(args[0], args[1])
        elif len(args) == 1:
            if args[0] < 1 or args[0] > 54:
                raise ValueError("Out of range")

            num = ceil(args[0] / 4) + 2
            suit = (args[0] - 1) % 4# 得到扑克牌
            suit = Poker.__suitType[suit]
            num = Poker.__rePokerMap[num]# 得到对应的键
            self.__init(num, suit)

    def __init(self, num, suit):
        num = str(num).upper()# 将num转化为大写的字符串
        if num not in Poker.__pokerMap:# 如果键不存在，就触发异常
            raise KeyError("Error key!")

        self.num = num# 扑克牌的数字
        self.suit = str(suit).lower()# 扑克牌的花色
        if self.suit not in Poker.__suitType:# 如果牌的花色不存在，就触发异常
            raise ValueError("No such suit")

        if Poker.__pokerMap[self.num] >= 16 and (self.suit == 'club' or self.suit == 'diamond'):# 如果牌的号和牌的花色不匹配就触发异常
            raise ValueError("Num and suit doesn't match")

    @staticmethod
    def get_num_value(num):
        """
        获得牌的点数对应的数值
        :param num:
        :return:
        """
        return Poker.__pokerMap[num]

    @staticmethod
    def get_next_poker_num(num, gap):
        """
        获得相间为gap的下一个扑克的点数
        :param num: 当前扑克的点数
        :param gap: 相间的间隔
        :return: 间隔后扑克的点数
        """
        return Poker.__rePokerMap[Poker.__pokerMap[num] + gap]

    @staticmethod
    def get_order(poker):
        """
        :param poker: 扑克牌
        :return:      扑克牌对应的顺序
        """
        order = Poker.__pokerMap[poker.num] - 3
        if poker.suit == 'heart':
            order = order * 4 + 1
        elif poker.suit == 'spade':
            order = order * 4 + 2
        elif poker.suit == 'club':
            order = order * 4 + 3
        elif poker.suit == 'diamond':
            order = order * 4 + 4
        return order

    def __repr__(self):
        return str((self.num, self.suit))

    def __lt__(self, other):
        return Poker.__pokerMap[self.num] < Poker.__pokerMap[other.num]

    def __gt__(self, other):
        return Poker.__pokerMap[self.num] > Poker.__pokerMap[other.num]

    def __le__(self, other):
        return Poker.__pokerMap[self.num] <= Poker.__pokerMap[other.num]

    def __ge__(self, other):
        return Poker.__pokerMap[self.num] >= Poker.__pokerMap[other.num]

    def __eq__(self, other):
        return Poker.__pokerMap[self.num] == Poker.__pokerMap[other.num]

    def __ne__(self, other):
        return Poker.__pokerMap[self.num] != Poker.__pokerMap[other.num]

    def __add__(self, other):
        return Poker.__rePokerMap[Poker.__pokerMap[self.num] + other]

    def __sub__(self, other):
        return Poker.__rePokerMap[Poker.__pokerMap[self.num] - other]


class PokerNode:
    """
    用于存储当前牌状态的节点
    """
    def __init__(self, pokerState, parent = None, action = None):
        """
        :param pokerState:  当前手牌
        :param parent:      上一个阶段的手牌
        :param action:      上一个阶段到这一个阶段出的牌
        :param searchType: 搜索类型，包括每种牌型只找最长的情况"longest"，和所有可能出牌情况"all"
        """
        self.state = pokerState
        self.parent = parent
        self.__count_poker()
        self.step = 0
        self.action = action
        if parent:
            self.step = parent.step + 1
        if len(pokerState) > 0:
            self.possibleStep = OrderedDict()
            self.search_step()
        else:
            self.pathCost = self.step

    def __count_poker(self):
        """
        得到每个点数的扑克牌的的列表
        """
        self.pokerCnt = OrderedDict() # 存储扑克数量的字典
        for poker in self.state:# 计算不同扑克的数量
            try:
                self.pokerCnt[poker.num].append(poker)
            except KeyError:
                self.pokerCnt[poker.num] = [poker]

    def get_child(self, action):
        """
        得到新的节点
        :param action:  当前节点到新的节点
        :return:        新的节点
        """
        newState = list(self.state)
        try:
            for item in action:# 得到新的状态
                newState.remove(item)
        except TypeError:
            newState.remove(action)
        return PokerNode(newState, self, action)

    def path(self):
        """
        Returns list of nodes from this node to the root node
        """
        node, path_back = self, []
        path_back.append(node.action)
        node = node.parent
        while node:
            if node.action:
                path_back.append(node.action)
            node = node.parent
        return list(reversed(path_back))

    def search_step(self):
        """
        搜索所有可能的出牌步骤，将结果存在self.possibleStep中
        self.possibleStep为有序字典，以便于后续出牌
        将启发函数值存入self.pathCost中
        """
        largestCnt = 0
        self.possibleStep['three straight'] = []
        self.possibleStep['three straight with gap'] = []
        self.possibleStep['pair straight'] = []
        self.possibleStep['pair straight with gap'] = []
        self.possibleStep['single straight'] = []
        self.possibleStep['single straight with gap'] = []
        self.possibleStep['four with two single'] = []
        self.possibleStep['four with two pair'] = []
        self.possibleStep['three with pair'] = []
        self.possibleStep['three with single'] = []
        self.possibleStep['four'] = []
        self.possibleStep['three'] = []
        self.possibleStep['pair'] = []
        self.possibleStep['single'] = [] # 一张一张出
        for length in range(1, 5):
            for num in self.pokerCnt:
                if len(self.pokerCnt[num]) == length:
                    self.possibleStep['single'].append(self.pokerCnt[num][0])
        if len(self.possibleStep['single']):
            largestCnt = 1

        for num in self.pokerCnt: # 寻找可以两张一起出的组合
            lst = self.pokerCnt[num]
            if len(lst) == 2:
                if largestCnt < 2:
                    largestCnt = 2
                self.possibleStep['pair'].append(lst)

        for num in self.pokerCnt:  # 寻找可以两张一起出的组合
            lst = self.pokerCnt[num]
            if len(lst) == 3:
                if largestCnt < 3:
                    largestCnt = 3
                self.possibleStep['three'].append(lst)
                self.possibleStep['pair'].append(lst[0: 2])

        for num in self.pokerCnt:  # 寻找可以两张一起出的组合
            lst = self.pokerCnt[num]
            if len(lst) == 4:
                if largestCnt < 4:
                    largestCnt = 4
                self.possibleStep['four'].append(lst)
                self.possibleStep['three'].append(lst[0: 3])

        for item in self.possibleStep['three']:
            for single in self.possibleStep['single']:# 寻找三带一的组合
                if single != item[0]:
                    if largestCnt < 4:
                        largestCnt = 4
                    self.possibleStep['three with single'].append(item + [single])
            for pair in self.possibleStep['pair']:# 寻找三带二组合
                if pair[0] != item[0] and pair[0].num != 'JOKER': # 保证三带二的一对牌不同于三张牌，火箭不算对子
                    if largestCnt < 5:
                        largestCnt = 5
                    self.possibleStep['three with pair'].append(item + pair)

        for item in self.possibleStep['four']:
            for single in self.possibleStep['single']:# 寻找四带二
                if single != item[0]:
                    for single2 in self.possibleStep['single'][self.possibleStep['single'].index(single) + 1:]:
                        if single2 != item[0]:
                            if largestCnt < 6:
                                largestCnt = 6
                            self.possibleStep['four with two single'].append(item + [single] + [single2])
            for pair in self.possibleStep['pair']:# 寻找四带二对
                if pair[0] != item[0] and pair[0].num != 'JOKER':
                    if largestCnt < 6:
                        largestCnt = 6
                    self.possibleStep['four with two single'].append(item + pair)
                    for pair2 in self.possibleStep['pair'][self.possibleStep['pair'].index(pair) + 1:]:
                        if pair2[0] != item[0] and pair2[0].num != 'JOKER':
                            if largestCnt < 8:
                                largestCnt = 8
                            self.possibleStep['four with two pair'].append(item + pair + pair2)
                elif pair[0] != item[0] and pair[0].num == 'JOKER':
                    if largestCnt < 6:
                        largestCnt = 6
                    self.possibleStep['four with two single'].append(item + pair)

        for num in self.pokerCnt:
            if Poker.get_num_value(num) >= 11:# 对于大于以J的扑克牌作为开始的顺子不可能存在
                break
            straightLst = [self.pokerCnt[num][0]]# 存储顺子的list
            while True:
                nextNum = Poker.get_next_poker_num(num, 1)
                num = nextNum
                if num in self.pokerCnt:# 如果下一个对应点数的牌存在，就存入顺子列表中
                    if num == '2' or num == 'JOKER':# 2和双王不算在顺子里
                        break
                    straightLst.append(self.pokerCnt[num][0])
                else:# 如果不在，就跳出循环
                    break
            while len(straightLst) >= 5:# 如果一个顺子中的牌数大于等于5，就存入可能步骤中
                self.possibleStep['single straight'].append(list(straightLst))
                straightLst.pop(len(straightLst) - 1)
        if not self.possibleStep['single straight']:
            self.possibleStep.pop('single straight')

        # 间隔单顺子
        for num in range(3, 7):
            num = str(num)
            if num not in self.pokerCnt:# 如果不存在在当前的牌中，就到下一次
                continue
            gapStraightLst = [self.pokerCnt[num][0]]
            while True:
                nextNum = Poker.get_next_poker_num(num, 2)
                num = nextNum
                if num in self.pokerCnt:  # 如果下一个对应点数的牌存在，就存入顺子列表中
                    if num == '2' or num == 'JOKER':  # 2和双王不算在顺子里
                        break
                    gapStraightLst.append(self.pokerCnt[num][0])
                else:  # 如果不在，就跳出循环
                    break
            while len(gapStraightLst) >= 5:  # 如果一个顺子中的牌数大于等于5，就存入可能步骤中
                self.possibleStep['single straight with gap'].append(list(gapStraightLst))
                gapStraightLst.pop(len(gapStraightLst) - 1)
        if not self.possibleStep['single straight with gap']:
            self.possibleStep.pop('single straight with gap')

        # 双顺子
        for num in self.pokerCnt:
            if Poker.get_num_value(num) >= 13:# 对于大于以K的扑克牌作为开始的顺子不可能存在
                break
            if len(self.pokerCnt[num]) < 2:# 如果当前对子不存在
                continue
            pairStraightLst = [self.pokerCnt[num][0], self.pokerCnt[num][1]]
            while True:
                nextNum = Poker.get_next_poker_num(num, 1)
                num = nextNum
                if num in self.pokerCnt:  # 如果下一个对应点数的牌存在，且为对子，就存入list中
                    if len(self.pokerCnt[num]) < 2:
                        break
                    if num == '2' or num == 'JOKER':  # 2和双王不算在顺子里
                        break
                    pairStraightLst.append(self.pokerCnt[num][0])
                    pairStraightLst.append(self.pokerCnt[num][1])
                else:  # 如果不在，就跳出循环
                    break
            while len(pairStraightLst) >= 6:  # 如果一个顺子中的牌数大于等于3，就存入可能步骤中
                self.possibleStep['pair straight'].append(list(pairStraightLst))
                pairStraightLst.pop(len(pairStraightLst) - 1)
                pairStraightLst.pop(len(pairStraightLst) - 1)
        if not self.possibleStep['pair straight']:
            self.possibleStep.pop('pair straight')

        # 间隔双顺子
        for num in self.pokerCnt:
            if Poker.get_num_value(num) >= 10:# 对于大于以10的扑克牌作为开始的顺子不可能存在
                break
            if len(self.pokerCnt[num]) < 2:# 如果当前对子不存在
                continue
            gapPairStraightLst = [self.pokerCnt[num][0], self.pokerCnt[num][1]]
            while True:
                nextNum = Poker.get_next_poker_num(num, 2)
                num = nextNum
                if num in self.pokerCnt:  # 如果下一个对应点数的牌存在，且为对子，就存入list中
                    if len(self.pokerCnt[num]) < 2:
                        break
                    if num == '2' or num == 'JOKER':  # 2和双王不算在顺子里
                        break
                    gapPairStraightLst.append(self.pokerCnt[num][0])
                    gapPairStraightLst.append(self.pokerCnt[num][1])
                else:  # 如果不在，就跳出循环
                    break
            while len(gapPairStraightLst) >= 6:  # 如果一个顺子中的牌数大于等于6，就存入可能步骤中
                self.possibleStep['pair straight with gap'].append(list(gapPairStraightLst))
                gapPairStraightLst.pop(len(gapPairStraightLst) - 1)
                gapPairStraightLst.pop(len(gapPairStraightLst) - 1)
        if not self.possibleStep['pair straight with gap']:
            self.possibleStep.pop('pair straight with gap')

        # 三顺子
        for num in self.pokerCnt:
            if Poker.get_num_value(num) >= 14:# 对于大于以A的扑克牌作为开始的顺子不可能存在
                break
            if len(self.pokerCnt[num]) < 3:  # 如果当前对子不存在
                continue
            threeStraightLst = [self.pokerCnt[num][0], self.pokerCnt[num][1], self.pokerCnt[num][2]]
            while True:
                nextNum = Poker.get_next_poker_num(num, 1)
                num = nextNum
                if num in self.pokerCnt:  # 如果下一个对应点数的牌存在，且为对子，就存入list中
                    if len(self.pokerCnt[num]) < 3:
                        break
                    if num == '2' or num == 'JOKER':  # 2和双王不算在顺子里
                        break
                    threeStraightLst.append(self.pokerCnt[num][0])
                    threeStraightLst.append(self.pokerCnt[num][1])
                    threeStraightLst.append(self.pokerCnt[num][2])
                else:  # 如果不在，就跳出循环
                    break
            while len(threeStraightLst) >= 6:  # 如果一个顺子中的牌数大于等于6，就存入可能步骤中
                self.possibleStep['three straight'].append(list(threeStraightLst))
                threeStraightLst.pop(len(threeStraightLst) - 1)
                threeStraightLst.pop(len(threeStraightLst) - 1)
                threeStraightLst.pop(len(threeStraightLst) - 1)

        # 间隔三顺子
        for num in self.pokerCnt:
            if Poker.get_num_value(num) >= 13:# 对于大于以K的扑克牌作为开始的顺子不可能存在
                break
            if len(self.pokerCnt[num]) < 3:  # 如果当前对子不存在
                continue
            gapThreeStraightLst = [self.pokerCnt[num][0], self.pokerCnt[num][1], self.pokerCnt[num][2]]
            while True:
                nextNum = Poker.get_next_poker_num(num, 2)
                num = nextNum
                if num in self.pokerCnt:  # 如果下一个对应点数的牌存在，且为对子，就存入list中
                    if len(self.pokerCnt[num]) < 3:
                        break
                    if num == '2' or num == 'JOKER':  # 2和双王不算在顺子里
                        break
                    gapThreeStraightLst.append(self.pokerCnt[num][0])
                    gapThreeStraightLst.append(self.pokerCnt[num][1])
                    gapThreeStraightLst.append(self.pokerCnt[num][2])
                else:  # 如果不在，就跳出循环
                    break
            while len(gapThreeStraightLst) >= 6:  # 如果一个顺子中的牌数大于等于6，就存入可能步骤中
                self.possibleStep['three straight with gap'].append(list(gapThreeStraightLst))
                gapThreeStraightLst.pop(len(gapThreeStraightLst) - 1)
                gapThreeStraightLst.pop(len(gapThreeStraightLst) - 1)
                gapThreeStraightLst.pop(len(gapThreeStraightLst) - 1)
        if not self.possibleStep['three straight']:
            self.possibleStep.pop('three straight')
        if not self.possibleStep['three straight with gap']:
            self.possibleStep.pop('three straight with gap')

        self.pathCost = self.step + ceil(len(self.state) / largestCnt)

    def __len__(self):
        return len(self.state)

    def __lt__(self, other):
        return self.pathCost < other.pathCost

    def __gt__(self, other):
        return self.pathCost > other.pathCost

    def __eq__(self, other):
        return self.state == other.state

    def __ne__(self, other):
        return self.state != other.state

    def __repr__(self):
        return str(self.state)


class PokerPlayer:
    """
    用于处理斗地主的问题
    """
    def __init__(self):
        self.score = -2 # 初始化score，用于第二问的求解
        self.path = None # 出牌步骤
        self.step = 0 # 初始化出牌步数

    def deal_random(self, pokerCnt):
        """
        按照牌的数量随机发牌
        :param pokerCnt: 发牌的数量
        结果存在self.initNode中
        self.curNode设置为self.initNode，用于第三问两个玩家对战
        """
        dealOrder = list(range(1, 55))# 得到随机的发牌顺序
        random.shuffle(dealOrder)
        initPoker = []# 初始的扑克牌列表
        for i in range(pokerCnt):
            initPoker.append(Poker(dealOrder[i]))
        initPoker.sort()
        self.initNode = PokerNode(initPoker)
        self.curNode = self.initNode

    def deal_specified(self, pokerLst):
        """
        指定牌型的发牌，不用于第三问两个对战
        :param pokerLst:    指定的扑克牌序列，每个扑克牌用一个点数加花色的元组进行
        结果存在self.initNode中
        """
        initPoker = []
        for item in pokerLst:
            initPoker.append(Poker(item[0], item[1]))
        initPoker.sort()
        self.initNode = PokerNode(initPoker)
        self.curNode = self.initNode

    def get_init_order(self):
        """
        得到初始牌的顺序，即将扑克牌的点数和花色转成1~54之间的数字
        :return: 初始牌的顺序序列
        """
        pokerOrderLst = []
        for item in self.initNode.state:
            pokerOrderLst.append(Poker.get_order(item))
        return pokerOrderLst

    def solve_without_score(self):
        """
        用最少的步骤出完牌，使用的是A*算法
        出牌步骤顺序存在self.path中
        出牌的步数存在self.step中
        """
        nodeQ = PriorityQueue(self.initNode)
        while True:
            curNode = nodeQ.pop()  # 提取代价最短的状态
            if len(curNode) == 0:
                self.path = curNode.path()
                self.step = len(self.path)
                break
            for kind in curNode.possibleStep:
                if kind == 'four with two single':
                    if len(curNode.possibleStep['four']) > 1:# 考虑四带四
                        for idx1 in range(0, len(curNode.possibleStep['four'])):
                            for idx2 in range(idx1 + 1, len(curNode.possibleStep['four'])):
                                nextNode = curNode.get_child(curNode.possibleStep['four'][idx1]
                                                             + curNode.possibleStep['four'][idx2])
                                idx = nodeQ.find(nextNode)
                                if idx is None:  # 如果不存在于开节点表中，就压入开节点表
                                    nodeQ.push(nextNode)
                                else:  # 如果存在，就根据代价的大小判断是否需要替换
                                    nodeQ.compare_and_replace(idx, nextNode)
                    break
                for action in curNode.possibleStep[kind]:
                    nextNode = curNode.get_child(action)
                    idx = nodeQ.find(nextNode)
                    if idx is None:  # 如果不存在于开节点表中，就压入开节点表
                        nodeQ.push(nextNode)
                    else:  # 如果存在，就根据代价的大小判断是否需要替换
                        nodeQ.compare_and_replace(idx, nextNode)

            while len(curNode):
                kindLst = []# 不出所有顺子
                for kind in curNode.possibleStep:
                    if kind == 'four with two single':
                        break
                    kindLst.append(kind)
                for kind in kindLst:
                    curNode.possibleStep.pop(kind)

                for kind in curNode.possibleStep:
                    if curNode.possibleStep[kind]:  # 出当前可能的牌
                        if kind == 'four with two single':
                            singleNum2 = curNode.possibleStep[kind][0][5].num
                            if len(curNode.pokerCnt[singleNum2]) > 1 and curNode.possibleStep['four with two pair']:
                                pairNum1 = curNode.possibleStep['four with two pair'][0][4].num
                                if len(curNode.pokerCnt[pairNum1]) == 2:
                                    nextNode = curNode.get_child(curNode.possibleStep['four with two pair'][0])
                                    curNode = nextNode
                                    break
                        elif kind == 'three with pair':
                            pairNum = curNode.possibleStep[kind][0][3].num
                            if len(curNode.pokerCnt[pairNum]) > 2:
                                if curNode.possibleStep['three with single']:
                                    singleNum = curNode.possibleStep['three with single'][0][3].num
                                    if len(curNode.pokerCnt[singleNum]) == 1:
                                        nextNode = curNode.get_child(curNode.possibleStep['three with single'][0])
                                        curNode = nextNode
                                        break
                        nextNode = curNode.get_child(curNode.possibleStep[kind][0])
                        curNode = nextNode
                        break
            idx = nodeQ.find(curNode)
            if idx is None:  # 如果不存在于开节点表中，就压入开节点表
                nodeQ.push(curNode)
            else:  # 如果存在，就根据代价的大小判断是否需要替换
                nodeQ.compare_and_replace(idx, curNode)

    def solve_with_score(self, curNode, stepCnt, value):
        """
        依据score进行优化，使用深搜
        最终score存入self.score中
        出牌步骤顺序存在self.path中
        出牌的步数存在self.step中
        """
        if len(curNode) == 0:
            score = -1
            try:
                score = log(value, stepCnt)
            except ValueError: # value为0
                score = -1
            except ZeroDivisionError: # stepCnt为1，改为1.01
                score = log(value, 1.01)
            finally:
                if score > self.score: # 如果当前的score更高，就用新的score和path进行更新
                    self.score = score
                    self.path = curNode.path()
                    self.step = len(self.path)
            return
        # else:
        #     score = -1
        #     try:
        #         score = log(value, stepCnt)
        #     except ValueError:  # value为0
        #         score = -1
        #     except ZeroDivisionError:  # stepCnt为1，改为1.01
        #         score = log(value, 1.01)
        #     finally:
        #         if score < self.score:
        #             return
        for kind in curNode.possibleStep:
            if kind == 'four with two single':
                if len(curNode.possibleStep['four']) > 1:  # 考虑四带四
                    for idx1 in range(0, len(curNode.possibleStep['four'])):
                        for idx2 in range(idx1 + 1, len(curNode.possibleStep['four'])):
                            nextNode = curNode.get_child(curNode.possibleStep['four'][idx1]
                                                         + curNode.possibleStep['four'][idx2])
                            newValue = value + 4
                            self.solve_with_score(nextNode, stepCnt + 1, newValue)
                break
            for action in curNode.possibleStep[kind]:
                if kind == 'three straight' or kind == 'three straight with gap': # 如果是三顺子，则value加7
                    newValue = value + 7
                elif kind == 'pair straight' or kind == 'pair straight with gap': # 如果是双顺子，则value加6
                    newValue = value + 6
                elif kind == 'single straight' or kind == 'single straight with gap': # 如果是单顺子，则value加5
                    newValue = value + 5

                nextNode = curNode.get_child(action)
                self.solve_with_score(nextNode, stepCnt + 1, newValue)

        while len(curNode):
            kindLst = []  # 不出所有顺子
            for kind in curNode.possibleStep:
                if kind == 'four with two single':
                    break
                kindLst.append(kind)
            for kind in kindLst:
                curNode.possibleStep.pop(kind)

            for kind in curNode.possibleStep:
                if curNode.possibleStep[kind]:  # 出当前可能的牌
                    if kind == 'four with two single':
                        singleNum2 = curNode.possibleStep[kind][0][5].num
                        if len(curNode.pokerCnt[singleNum2]) > 1:
                            if curNode.possibleStep['four with two pair']:
                                pairNum2 = curNode.possibleStep['four with two pair'][0][6].num
                                if len(curNode.pokerCnt[pairNum2]) == 2:
                                    nextNode = curNode.get_child(curNode.possibleStep['four with two pair'][0])
                                    curNode = nextNode
                                    stepCnt += 1
                                    value += 4
                                    break
                                else:
                                    self._deep_search_with_score(curNode, stepCnt, value)
                            else:
                                self._deep_search_with_score(curNode, stepCnt, value)
                    elif kind == 'three with pair':
                        pairNum = curNode.possibleStep[kind][0][3].num
                        if len(curNode.pokerCnt[pairNum]) > 2:
                            if curNode.possibleStep['three with single']:
                                singleNum = curNode.possibleStep['three with single'][0][3].num
                                if len(curNode.pokerCnt[singleNum]) == 1:
                                    nextNode = curNode.get_child(curNode.possibleStep['three with single'][0])
                                    curNode = nextNode
                                    stepCnt += 1
                                    value += 3
                                    break
                                else:
                                    self._deep_search_with_score(curNode, stepCnt, value)
                            else:
                                self._deep_search_with_score(curNode, stepCnt, value)
                    nextNode = curNode.get_child(curNode.possibleStep[kind][0])
                    curNode = nextNode
                    stepCnt += 1
                    if kind == 'four with two pair' or kind == 'four with two single':  # 如果是四带一对或者四带两对，则value加4
                        value += 4
                    elif (kind == 'three' or kind == 'four'
                            or kind == 'three with pair' or kind == 'three with single'):
                        value += 3
                    break
        self.solve_with_score(curNode, stepCnt, value)

    def _deep_search_with_score(self, curNode, stepCnt, value):
        """
        不包含顺子的深搜，辅助实现上一个函数的功能
        """
        if len(curNode) == 0:
            score = -1
            try:
                score = log(value, stepCnt)
            except ValueError: # value为0
                score = -1
            except ZeroDivisionError: # stepCnt为1
                score = 0
            finally:
                if score > self.score: # 如果当前的score更高，就用新的score和path进行更新
                    self.score = score
                    self.path = curNode.path()
                    self.step = len(self.path)
            return
        # else:
        #     score = -1
        #     try:
        #         score = log(value, stepCnt)
        #     except ValueError:  # value为0
        #         score = -1
        #     except ZeroDivisionError:  # stepCnt为1，改为1.01
        #         score = log(value, 1.01)
        #     finally:
        #         if score < self.score:
        #             return
        kindLst = []  # 不出所有顺子
        for kind in curNode.possibleStep:
            if kind == 'four with two single':
                break
            kindLst.append(kind)
        for kind in kindLst:
            curNode.possibleStep.pop(kind)

        tmpCnt = 0
        for kind in curNode.possibleStep:
            if kind == 'pair':
                break
            for action in curNode.possibleStep[kind]:
                tmpCnt += 1
                if kind == 'four with two pair' or kind == 'four with two single':  # 如果是四带一对或者四带两对，则value加4
                    newValue = value + 4
                elif (kind == 'three' or kind == 'four'
                      or kind == 'three with pair' or kind == 'three with single'):
                    newValue = value + 3

                nextNode = curNode.get_child(action)
                self._deep_search_with_score(nextNode, stepCnt + 1, newValue)
        if tmpCnt == 0:
            while len(curNode):
                for kind in curNode.possibleStep:
                    if curNode.possibleStep[kind]:  # 出当前可能的牌
                        nextNode = curNode.get_child(curNode.possibleStep[kind][0])
                        curNode = nextNode
                        stepCnt += 1
                        break
            self._deep_search_with_score(curNode, stepCnt, value)

    def gaming(self, opponentAction):
        """
        1v1对战用的函数
        :param opponentAction:  元组类型，(对手出的牌的类型, 实际出的牌的数组)
        :return:                (自己出的牌的类型, 实际出的牌的数组)
        """
        if not opponentAction: # 如果对手没有出牌，就按可能出牌种类的顺序进行出牌
            for kind in self.curNode.possibleStep:
                if self.curNode.possibleStep[kind]:
                    action = self.curNode.possibleStep[kind][0]
                    self.curNode = self.curNode.get_child(action)
                    return kind, action
        else: # 如果对手出牌了，就根据对手出牌的类型在自己所有出牌可能中进行搜索
            kind = opponentAction[0]
            if kind in self.curNode.possibleStep:
                for action in self.curNode.possibleStep[kind]:
                    if kind != 'single':
                        # 根据情况判断是否可以出牌
                        if len(action) == len(opponentAction[1]) and action[0] > opponentAction[1][0]:
                            self.curNode = self.curNode.get_child(action)
                            return kind, action
                    else:
                        if action > opponentAction[1]:
                            self.curNode = self.curNode.get_child(action)
                            return kind, action
            elif kind == 'four with two pair':
                if len(self.curNode.possibleStep['four']) > 1:
                    if self.curNode.possibleStep['four'][0][0] > opponentAction[1][0]:
                        action = self.curNode.possibleStep['four'][0] + self.curNode.possibleStep['four'][1]
                        return kind, action
                    else:
                        for four in self.curNode.possibleStep['four']:
                            if four[0] > opponentAction[1][0]:
                                action = self.curNode.possibleStep['four'][0] + four
                                return kind, action
        return None


if __name__ == "__main__":
    player = PokerPlayer()
    player.deal_random(30)
    #player.deal_specified([('3', 'heart'), ('4', 'heart'), ('5', 'heart'), ('6', 'heart'), ('6', 'spade'), ('7', 'heart'), ('8', 'heart'), ('8', 'club'), ('8', 'spade')])
    #player.deal_specified([('3', 'heart'), ('3', 'spade'), ('3', 'club'), ('4', 'heart'), ('4', 'spade'), ('4', 'club'), ('5', 'heart'), ('5', 'spade'), ('5', 'club'), ('7', 'heart'), ('8', 'heart')])
    # player.deal_specified(
    #     [('3', 'heart'), ('4', 'heart'), ('4', 'spade'), ('4', 'club'), ('6', 'heart'), ('6', 'spade'), ('6', 'club'),
    #      ('7', 'heart'), ('8', 'heart'), ('9', 'heart'), ('9', 'spade'),  ('9', 'heart'), ('9', 'spade'),
    #      ('J', 'heart'), ('J', 'spade'), ('J', 'club'), ('J', 'diamond'), ('Q', 'spade'), ('K', 'club'),('K', 'heart'), ('A', 'club')])
    #player.solve_without_score()
    player.solve_with_score(player.initNode, 0, 0)
    # player2 = PokerPlayer()
    # player2.deal_random(20)
    # print(player.initNode)
    # print(player2.initNode)
    # action = None
    # while player.curNode and player2.curNode:
    #     action = player.gaming(action)
    #     print("player1:")
    #     print(action)
    #     action = player2.gaming(action)
    #     print("player2:")
    #     print(action)

    print(player.initNode.state)
    for item in player.path:
        print(item)
    print(player.score)
