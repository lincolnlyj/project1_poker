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
    大小王均为JOKER
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
    def __init__(self, pokerState, parent = None, action = None, searchType = "all"):
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
            self.search_step(searchType)
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

    def get_child(self, action, searchType):
        newState = list(self.state)
        try:
            for item in action:# 得到新的状态
                newState.remove(item)
        except TypeError:
            newState.remove(action)
        return PokerNode(newState, self, action, searchType)

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

    def search_step(self, searchType):
        """
        :param searchType: 搜索类型，包括每种牌型只找最长的情况"longest"，和所有可能出牌情况"all"
        :return:
        """
        if searchType != 'longest' and searchType != 'all':
            raise ValueError('Parameter searchType is wrong')
        largestCnt = 0
        self.possibleStep['three straight'] = []
        self.possibleStep['three straight with gap'] = []
        self.possibleStep['pair straight'] = []
        self.possibleStep['pair straight with gap'] = []
        self.possibleStep['single straight'] = []
        self.possibleStep['single straight with gap'] = []
        self.possibleStep['four with two pair'] = []
        self.possibleStep['four with two single'] = []
        self.possibleStep['three with pair'] = []
        self.possibleStep['three with single'] = []
        self.possibleStep['four'] = []
        self.possibleStep['three'] = []
        self.possibleStep['pair'] = []
        self.possibleStep['single'] = [] # 一张一张出
        for num in self.pokerCnt:
            self.possibleStep['single'].append(self.pokerCnt[num][0])
        if len(self.possibleStep['single']):
            largestCnt = 1

        for num in self.pokerCnt: # 寻找可以两张一起出的组合
            lst = self.pokerCnt[num]
            if len(lst) == 4:
                if largestCnt < 4:
                    largestCnt = 4
                self.possibleStep['four'].append(lst)
                self.possibleStep['three'].append(lst[0: 3])
                # if searchType == 'longest': # 如果按照每种拍最长的可能性进行搜索，就去掉单牌
                #     for item in lst:
                #         self.possibleStep['single'].remove(item) # 去掉可以四张一起出的单张牌
                # else:
                #     self.possibleStep['pair'].append(lst[0: 2])
            elif len(lst) == 3:
                if largestCnt < 3:
                    largestCnt = 3
                self.possibleStep['three'].append(lst)
                self.possibleStep['pair'].append(lst[0: 2])
                # if searchType == 'longest':  # 如果按照每种拍最长的可能性进行搜索，就去掉单牌
                #     for item in lst:
                #         self.possibleStep['single'].remove(item)  # 去掉可以三张一起出的单张牌
            elif len(lst) == 2:
                if largestCnt < 2:
                    largestCnt = 2
                self.possibleStep['pair'].append(lst)

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

        lastLst = None# 上一个顺子
        for num in self.pokerCnt:
            if Poker.get_num_value(num) >= 11:# 对于大于以J的扑克牌作为开始的顺子不可能存在
                break
            if lastLst and searchType == 'longest':# 当searchType为"longest"时，不保存有重叠的顺子
                if Poker(num, 'heart') in lastLst:
                    continue
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
            if searchType == 'all': # 如果搜索所有出牌可能
                while len(straightLst) >= 5:# 如果一个顺子中的牌数大于等于5，就存入可能步骤中
                    self.possibleStep['single straight'].append(list(straightLst))
                    straightLst.pop(len(straightLst) - 1)
            else: # 如果搜索最长出牌可能
                if len(straightLst) >= 5:
                    if largestCnt < len(straightLst):
                        largestCnt = len(straightLst)
                    self.possibleStep['single straight'].append(list(straightLst))
                    lastLst = straightLst
                    straightLst.pop(0)
                    while len(straightLst) >= 5:# 如果一个顺子中的牌数大于等于5，就存入可能步骤中
                        self.possibleStep['single straight'].append(list(straightLst))
                        straightLst.pop(0)
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
            if searchType == 'all':  # 如果搜索所有出牌可能
                while len(gapStraightLst) >= 5:  # 如果一个顺子中的牌数大于等于5，就存入可能步骤中
                    self.possibleStep['single straight with gap'].append(list(gapStraightLst))
                    gapStraightLst.pop(len(gapStraightLst) - 1)
            else:
                if len(gapStraightLst) >= 5:  # 如果一个顺子中的牌数大于等于5，就存入可能步骤中
                    if largestCnt < len(gapStraightLst):
                        largestCnt = len(gapStraightLst)
                    self.possibleStep['single straight with gap'].append(list(gapStraightLst))
                    gapStraightLst.pop(0)
                    while len(gapStraightLst) >= 5:  # 如果一个顺子中的牌数大于等于5，就存入可能步骤中
                        self.possibleStep['single straight with gap'].append(list(gapStraightLst))
                        gapStraightLst.pop(0)
        if not self.possibleStep['single straight with gap']:
            self.possibleStep.pop('single straight with gap')

        # 双顺子
        lastLst = None
        for num in self.pokerCnt:
            if Poker.get_num_value(num) >= 13:# 对于大于以K的扑克牌作为开始的顺子不可能存在
                break
            if len(self.pokerCnt[num]) < 2:# 如果当前对子不存在
                continue
            if lastLst and searchType == 'longest':# 当searchType为"longest"时，不保存有重叠的顺子
                if Poker(num, 'heart') in lastLst:
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
            if searchType == 'all':
                while len(pairStraightLst) >= 6:  # 如果一个顺子中的牌数大于等于3，就存入可能步骤中
                    self.possibleStep['pair straight'].append(list(pairStraightLst))
                    pairStraightLst.pop(len(pairStraightLst) - 1)
                    pairStraightLst.pop(len(pairStraightLst) - 1)
            else:
                if len(pairStraightLst) >= 6:  # 如果一个顺子中的牌数大于等于3，就存入可能步骤中
                    if largestCnt < len(pairStraightLst):
                        largestCnt = len(pairStraightLst)
                    self.possibleStep['pair straight'].append(list(pairStraightLst))
                    lastLst = pairStraightLst
                    pairStraightLst.pop(0)
                    pairStraightLst.pop(0)
                    while len(pairStraightLst) >= 6:  # 如果一个顺子中的牌数大于等于3，就存入可能步骤中
                        self.possibleStep['pair straight'].append(list(pairStraightLst))
                        pairStraightLst.pop(0)
                        pairStraightLst.pop(0)
        if not self.possibleStep['pair straight']:
            self.possibleStep.pop('pair straight')

        # 间隔双顺子
        for num in self.pokerCnt:
            if Poker.get_num_value(num) >= 10:# 对于大于以10的扑克牌作为开始的顺子不可能存在
                break
            if len(self.pokerCnt[num]) < 2:# 如果当前对子不存在
                continue
            if lastLst and searchType == 'longest':# 当searchType为"longest"时，不保存有重叠的顺子
                if Poker(num, 'heart') in lastLst:
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
            if searchType == 'all':
                while len(gapPairStraightLst) >= 6:  # 如果一个顺子中的牌数大于等于6，就存入可能步骤中
                    self.possibleStep['pair straight with gap'].append(list(gapPairStraightLst))
                    gapPairStraightLst.pop(len(gapPairStraightLst) - 1)
                    gapPairStraightLst.pop(len(gapPairStraightLst) - 1)
            else:
                if len(gapPairStraightLst) >= 6:  # 如果一个顺子中的牌数大于等于6，就存入可能步骤中
                    if largestCnt < len(gapPairStraightLst):
                        largestCnt = len(gapPairStraightLst)
                    self.possibleStep['pair straight with gap'].append(list(gapPairStraightLst))
                    lastLst = gapPairStraightLst
                    gapPairStraightLst.pop(0)
                    gapPairStraightLst.pop(0)
                    while len(gapPairStraightLst) >= 6:  # 如果一个顺子中的牌数大于等于3，就存入可能步骤中
                        self.possibleStep['pair straight with gap'].append(list(gapPairStraightLst))
                        gapPairStraightLst.pop(0)
                        gapPairStraightLst.pop(0)
        if not self.possibleStep['pair straight with gap']:
            self.possibleStep.pop('pair straight with gap')

        # 三顺子
        lastLst = None
        for num in self.pokerCnt:
            if Poker.get_num_value(num) >= 14:# 对于大于以A的扑克牌作为开始的顺子不可能存在
                break
            if len(self.pokerCnt[num]) < 3:  # 如果当前对子不存在
                continue
            if lastLst and searchType == 'longest':# 当searchType为"longest"时，不保存有重叠的顺子
                if Poker(num, 'heart') in lastLst:
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
            if searchType == 'all':
                while len(threeStraightLst) >= 6:  # 如果一个顺子中的牌数大于等于6，就存入可能步骤中
                    self.possibleStep['three straight'].append(list(threeStraightLst))
                    threeStraightLst.pop(len(threeStraightLst) - 1)
                    threeStraightLst.pop(len(threeStraightLst) - 1)
                    threeStraightLst.pop(len(threeStraightLst) - 1)
            else:
                if len(threeStraightLst) >= 6:  # 如果一个顺子中的牌数大于等于6，就存入可能步骤中
                    if largestCnt < len(threeStraightLst):
                        largestCnt = len(threeStraightLst)
                    self.possibleStep['three straight'].append(list(threeStraightLst))
                    lastLst = threeStraightLst
                    if len(threeStraightLst) == 6: # 如果顺子的牌数等于6，就将三带一和三带二也考虑进来，避免出现非最小状态
                        for item in self.possibleStep['three with single']:
                            if item[0] == threeStraightLst[0] or item[0] == threeStraightLst[3]:
                                self.possibleStep['three straight'].append(item)
                        for item in self.possibleStep['three with pair']:
                            if item[0] == threeStraightLst[0] or item[0] == threeStraightLst[3]:
                                self.possibleStep['three straight'].append(item)

        # 间隔三顺子
        lastLst = None
        for num in self.pokerCnt:
            if Poker.get_num_value(num) >= 13:# 对于大于以K的扑克牌作为开始的顺子不可能存在
                break
            if len(self.pokerCnt[num]) < 3:  # 如果当前对子不存在
                continue
            if lastLst and searchType == 'longest':# 当searchType为"longest"时，不保存有重叠的顺子
                if Poker(num, 'heart') in lastLst:
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
            if searchType == 'all':
                while len(gapThreeStraightLst) >= 6:  # 如果一个顺子中的牌数大于等于6，就存入可能步骤中
                    self.possibleStep['three straight with gap'].append(list(gapThreeStraightLst))
                    gapThreeStraightLst.pop(len(gapThreeStraightLst) - 1)
                    gapThreeStraightLst.pop(len(gapThreeStraightLst) - 1)
                    gapThreeStraightLst.pop(len(gapThreeStraightLst) - 1)
            else:
                if len(gapThreeStraightLst) >= 6:  # 如果一个顺子中的牌数大于等于6，就存入可能步骤中
                    if largestCnt < len(gapThreeStraightLst):
                        largestCnt = len(gapThreeStraightLst)
                    self.possibleStep['three straight with gap'].append(list(gapThreeStraightLst))
                    lastLst = gapThreeStraightLst
                    if len(gapThreeStraightLst) == 6: # 如果顺子的牌数等于6，就将三带一和三带二也考虑进来，避免出现非最小状态
                        for item in self.possibleStep['three with single']:
                            if item[0] == gapThreeStraightLst[0] or item[0] == gapThreeStraightLst[3]:
                                if item not in self.possibleStep['three straight']:
                                    self.possibleStep['three straight with gap'].append(item)
                        for item in self.possibleStep['three with pair']:
                            if item[0] == gapThreeStraightLst[0] or item[0] == gapThreeStraightLst[3]:
                                if item not in self.possibleStep['three straight']:
                                    self.possibleStep['three straight with gap'].append(item)
        if not self.possibleStep['three straight'] and not self.possibleStep['three straight with gap']:
            self.possibleStep['three straight'] = self.possibleStep['three with single']\
                                                  + self.possibleStep['three with pair']
        if not self.possibleStep['three straight']:
            self.possibleStep.pop('three straight')
        if not self.possibleStep['three straight with gap']:
            self.possibleStep.pop('three straight with gap')

        self.pathCost = self.step + ceil(len(self.state) / largestCnt)

    def update_step(self):
        pass

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


class PokerProblem:
    """
    用于处理斗地主的问题
    """
    def __init__(self):
        self.score = -2 # 初始化score，用于第二问的求解
        self.path = None # 出牌步骤
        self.step = 0 # 初始化出牌步数

    def deal_random(self, pokerCnt):
        """
        :param pokerCnt: 发牌的数量
        :return:
        """
        dealOrder = list(range(1, 55))# 得到随机的发牌顺序
        random.shuffle(dealOrder)
        initPoker = []# 初始的扑克牌列表
        for i in range(pokerCnt):
            initPoker.append(Poker(dealOrder[i]))
        initPoker.sort()
        self.initNode = PokerNode(initPoker)

    def deal_specified(self, pokerLst):
        initPoker = []
        for item in pokerLst:
            initPoker.append(Poker(item[0], item[1]))
        initPoker.sort()
        self.initNode = PokerNode(initPoker)

    def solve_without_score(self):
        """
        用最少的步骤出完牌
        """
        nodeQ = PriorityQueue(self.initNode)
        while True:
            curNode = nodeQ.pop()  # 提取代价最短的状态
            if len(curNode) == 0:
                self.path = curNode.path()
                self.step = len(self.path)
                break
            for kind in curNode.possibleStep:
                if kind == 'four with two pair':
                    break
                for action in curNode.possibleStep[kind]:
                    nextNode = curNode.get_child(action, "all")
                    idx = nodeQ.find(nextNode)
                    if idx is None:  # 如果不存在于开节点表中，就压入开节点表
                        nodeQ.push(nextNode)
                    else:  # 如果存在，就根据代价的大小判断是否需要替换
                        nodeQ.compare_and_replace(idx, nextNode)
            while len(curNode):
                for kind in curNode.possibleStep:
                    if curNode.possibleStep[kind]:  # 出当前可能的牌
                        nextNode = curNode.get_child(curNode.possibleStep[kind][0], "all")
                        curNode = nextNode
                        break
            idx = nodeQ.find(curNode)
            if idx is None:  # 如果不存在于开节点表中，就压入开节点表
                nodeQ.push(curNode)
            else:  # 如果存在，就根据代价的大小判断是否需要替换
                nodeQ.compare_and_replace(idx, curNode)
            # tmpCnt = 0# 如果顺子，四带二这些牌型都没有，再出三带二三带一和其他牌
            # for kind in curNode.possibleStep:
            #     if kind == 'three with pair':
            #         break
            #     for action in curNode.possibleStep[kind]:
            #         tmpCnt += 1
            #         nextNode = curNode.get_child(action)
            #         idx = nodeQ.find(nextNode)
            #         if idx is None:  # 如果不存在于开节点表中，就压入开节点表
            #             nodeQ.push(nextNode)
            #         else:  # 如果存在，就根据代价的大小判断是否需要替换
            #             nodeQ.compare_and_replace(idx, nextNode)
            # if not tmpCnt:# 如果没有顺子，四带二等牌，就出三带一等其他类型的牌
            #     while len(curNode):
            #         for kind in curNode.possibleStep:
            #             if curNode.possibleStep[kind]:# 出当前可能的牌
            #                 nextNode = curNode.get_child(curNode.possibleStep[kind][0])
            #                 curNode = nextNode
            #                 break
            #     idx = nodeQ.find(curNode)
            #     if idx is None:  # 如果不存在于开节点表中，就压入开节点表
            #         nodeQ.push(curNode)
            #     else:  # 如果存在，就根据代价的大小判断是否需要替换
            #         nodeQ.compare_and_replace(idx, curNode)

    def solve_with_score(self, curNode, stepCnt, value):
        """
        依据score进行优化
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
        for kind in curNode.possibleStep:
            if kind == 'four with two pair':
                break
            for action in curNode.possibleStep[kind]:
                if kind == 'three straight' or kind == 'three straight with gap': # 如果是三顺子，则value加7
                    value += 7
                elif kind == 'pair straight' or kind == 'pair straight with gap': # 如果是双顺子，则value加6
                    value += 6
                elif kind == 'single straight' or kind == 'single straight with gap': # 如果是单顺子，则value加5
                    value += 5

                nextNode = curNode.get_child(action, 'all')
                self.solve_with_score(nextNode, stepCnt + 1, value)
        while len(curNode):
            for kind in curNode.possibleStep:
                if curNode.possibleStep[kind]:  # 出当前可能的牌
                    nextNode = curNode.get_child(curNode.possibleStep[kind][0], 'all')
                    curNode = nextNode
                    stepCnt += 1
                    if kind == 'four with two pair' or kind == 'four with two single':  # 如果是四带一对或者四带两对，则value加4
                        value += 4
                    elif (kind == 'three' or kind == 'four'
                            or kind == 'three with pair' or kind == 'three with single'):
                        value += 3
                    break
        self.solve_with_score(curNode, stepCnt, value)
        # tmpCnt = 0 # 如果顺子，四带二这些牌型都没有，再出三带二三带一和其他牌
        # for kind in curNode.possibleStep:
        #     if kind == 'three with pair':
        #         break
        #     for action in curNode.possibleStep[kind]:
        #         tmpCnt += 1
        #         if kind == 'three straight' or kind == 'three straight with gap': # 如果是三顺子，则value加7
        #             value += 7
        #         elif kind == 'pair straight' or kind == 'pair straight with gap': # 如果是双顺子，则value加6
        #             value += 6
        #         elif kind == 'single straight' or kind == 'single straight with gap': # 如果是单顺子，则value加5
        #             value += 5
        #         elif kind == 'four with two pair' or kind == 'four with two single': # 如果是四带一对或者四带两对，则value加4
        #             value += 4
        #         elif kind == 'three with pair' or kind == 'three with single': # 如果是三带一或者三带二，则value加3
        #             value += 3
        #
        #         nextNode = curNode.get_child(action)
        #         self.solve_with_score(nextNode, stepCnt + 1, value)
        # if not tmpCnt:  # 如果没有顺子，四带二等牌，就出三带一等其他类型的牌
        #     while len(curNode):
        #         for kind in curNode.possibleStep:
        #             if curNode.possibleStep[kind]:  # 出当前可能的牌
        #                 nextNode = curNode.get_child(curNode.possibleStep[kind][0])
        #                 curNode = nextNode
        #                 stepCnt += 1
        #                 if (kind == 'three' or kind == 'four'
        #                         or kind == 'three with pair' or kind == 'three with single'):
        #                     value += 3
        #                 break
        #     self.solve_with_score(curNode, stepCnt, value)


if __name__ == "__main__":
    problem = PokerProblem()
    problem.deal_random(2)
    #problem.deal_specified([('3', 'heart'), ('4', 'heart'), ('5', 'heart'), ('6', 'heart'), ('6', 'spade'), ('7', 'heart'), ('8', 'heart'), ('8', 'club'), ('8', 'spade')])
    #problem.deal_specified([('3', 'heart'), ('3', 'spade'), ('3', 'club'), ('4', 'heart'), ('4', 'spade'), ('4', 'club'), ('5', 'heart'), ('5', 'spade'), ('5', 'club'), ('7', 'heart'), ('8', 'heart')])
    #problem.solve_without_score()
    problem.solve_with_score(problem.initNode, 0, 0)

    print(problem.initNode.state)
    for item in problem.path:
        print(item)
    print(problem.score)