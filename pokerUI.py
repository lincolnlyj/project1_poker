# -*- coding=utf-8 -*-
from PyQt6.QtGui import QIcon, QGuiApplication, QPixmap, QPalette, QIntValidator
from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton, QGridLayout, QHBoxLayout, QWidget, QLabel, \
    QLineEdit, QMessageBox, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6 import QtCore
from poker import Poker
import sys
from process import Process
from math import floor


class MyQLabel(QLabel):
    # 可以点击的QLabel
    button_clicked_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(MyQLabel, self).__init__(parent)

    def mouseReleaseEvent(self, QMouseEvent):
        self.button_clicked_signal.emit()

    # 可在外部与槽函数连接
    def connect_customized_slot(self, func):
        self.button_clicked_signal.connect(func)


class PokerWindow(QMainWindow):
    """
    斗地主主窗口
    """

    def __init__(self):
        super().__init__()
        self.task = 0 # 当前的题目
        self.process = Process()
        self.resize(821, 472)
        self.setMinimumSize(821, 472)
        self.center()
        self.setWindowTitle("斗地主")
        self.setObjectName("MainWindow")
        self.setStyleSheet("#MainWindow{border-image:url(background.jpeg)}")  # 背景图片
        self.setWindowIcon(QIcon('icon.jpeg'))

        self.grid = QGridLayout(self)# 整个窗口的布局
        self.centerLayout = QVBoxLayout(self)# 中心区域的布局
        self.centerWidget = QWidget(self)# 放置中旬区域布局的Widget

        self.homeBtn = QPushButton("主页", self)
        self.homeBtn.hide()

        self.homeBtn.clicked.connect(self.clicked_home_btn)
        self.win = QWidget(self)
        self.__init_page()
        self.init_first_page()
        self.show()

    def __init_page(self):
        positions = [(i, j) for i in range(7) for j in range(7)]# 网格大小
        for pos in positions: # 创建网格布局
            if pos[0] == 3 and pos[1] == 3:
                self.grid.addWidget(self.centerWidget, *pos, Qt.AlignmentFlag.AlignHCenter |
                                    Qt.AlignmentFlag.AlignVCenter)
                continue
            if pos[0] == 0 and pos[1] == 6:
                self.grid.addWidget(self.homeBtn, *pos)
                continue
            self.grid.addWidget(QWidget(self), *pos)
        self.centerWidget.setLayout(self.centerLayout)
        self.win.setLayout(self.grid)
        self.setCentralWidget(self.win)

    def center(self):
        """
        居中显示窗口
        """
        frame = self.frameGeometry()
        centerPos = QGuiApplication.primaryScreen().availableGeometry().center()
        frame.moveCenter(centerPos)
        self.move(frame.topLeft())

    def init_first_page(self):
        """
        创建初始页面，选择题目
        """
        while self.centerLayout.count(): # 清除layout中的所有元素
            child = self.centerLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        firstTaskBtn = QPushButton("第一问", self)
        secondTaskBtn = QPushButton("第二问", self)
        thirdTaskBtn = QPushButton("第三问", self)
        firstTaskBtn.clicked.connect(self.clicked_task_btn)
        secondTaskBtn.clicked.connect(self.clicked_task_btn)
        thirdTaskBtn.clicked.connect(self.clicked_task_btn)
        self.centerLayout.addWidget(firstTaskBtn)
        self.centerLayout.addSpacing(20)
        self.centerLayout.addWidget(secondTaskBtn)
        self.centerLayout.addSpacing(20)
        self.centerLayout.addWidget(thirdTaskBtn)

    def init_deal_page(self):
        """
        发牌页面
        """
        while self.centerLayout.count():
            child = self.centerLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        randomBtn = QPushButton("随机发牌", self)
        randomBtn.clicked.connect(self.init_random_deal_page_task12)
        specifiedBtn = QPushButton("指定牌型", self)
        specifiedBtn.clicked.connect(self.init_specified_deal_page)
        self.centerLayout.addWidget(randomBtn)
        self.centerLayout.addSpacing(20)
        self.centerLayout.addWidget(specifiedBtn)

    def init_random_deal_page_task12(self):
        """
        第一二问随机发牌界面
        """
        while self.centerLayout.count():
            child = self.centerLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        inputHint = QLabel("请输入手牌数量: ")
        inputHint.setStyleSheet("color:white")
        self.pokerCntInput = QLineEdit(self)
        self.pokerCntInput.setValidator(QIntValidator(self))
        confirmBtn = QPushButton("确定")
        confirmBtn.clicked.connect(self.confirm_poker_cnt)
        self.centerLayout.addWidget(inputHint)
        self.centerLayout.addSpacing(20)
        self.centerLayout.addWidget(self.pokerCntInput)
        self.centerLayout.addSpacing(20)
        self.centerLayout.addWidget(confirmBtn)
        
    def init_random_deal_page_task3(self):
        """
        第三问随机发牌界面
        """
        while self.centerLayout.count():
            child = self.centerLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        player1InputHint = QLabel("请输入Player1手牌数量: ")
        player1InputHint.setStyleSheet("color:white")
        self.player1PokerCntInput = QLineEdit(self)
        self.player1PokerCntInput.setValidator(QIntValidator(self))
        player2InputHint = QLabel("请输入Player2手牌数量: ")
        player2InputHint.setStyleSheet("color:white")
        self.player2PokerCntInput = QLineEdit(self)
        self.player2PokerCntInput.setValidator(QIntValidator(self))
        confirmBtn = QPushButton("确定")
        confirmBtn.clicked.connect(self.confirm_poker_cnt_task3)
        self.centerLayout.addWidget(player1InputHint)
        self.centerLayout.addSpacing(20)
        self.centerLayout.addWidget(self.player1PokerCntInput)
        self.centerLayout.addSpacing(20)
        self.centerLayout.addWidget(player2InputHint)
        self.centerLayout.addSpacing(20)
        self.centerLayout.addWidget(self.player2PokerCntInput)
        self.centerLayout.addSpacing(20)
        self.centerLayout.addWidget(confirmBtn)

    def init_specified_deal_page(self):
        """
        自行选择牌数
        """
        while self.centerLayout.count():
            child = self.centerLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.pokerOrder = []
        self.pokerImgs = [0 for _ in range(55)]
        self.selectWidget = QWidget(self)
        self.selectWidget.setMaximumSize(self.width() - 160, self.height() - 80)
        selectLayout = QGridLayout(self.selectWidget)
        for order in range(1, 55):
            selBtn = QPushButton(Poker(order).num + " " + Poker(order).suit, self.selectWidget)
            selBtn.clicked.connect(self.sel_poker)
            selectLayout.addWidget(selBtn, floor((order - 1) / 4), (order - 1) % 4)
        self.selectWidget.setLayout(selectLayout)
        self.grid.addWidget(self.selectWidget, 3, 3)
        self.confirmBtn = QPushButton("确认", self.selectWidget)
        self.confirmBtn.clicked.connect(self.specified_deal_confirm)
        self.grid.addWidget(self.confirmBtn, 3, 6)

    def sel_poker(self):
        """
        选择某个poker后执行的函数
        """
        selBtn = self.sender()
        [num, suit] = selBtn.text().split(" ")
        self.pokerOrder.append(Poker.get_order(Poker(num, suit)))
        selBtn.hide()

    def specified_deal_confirm(self):
        """
        确认输入的特定poker后执行
        """
        self.selectWidget.deleteLater()
        self.confirmBtn.deleteLater()
        self.process.specified_deal(self.pokerOrder)
        for order in self.pokerOrder:
            pixmapLbl = QLabel(self)
            pixmapLbl.setFixedSize(102, 142)
            tmpPixmap = QPixmap("Cards\\" + str(order) + ".png")
            pixmapLbl.setScaledContents(True)
            pixmapLbl.setPixmap(tmpPixmap)
            self.pokerImgs[order] = pixmapLbl  # 扑克图片数组
        self.show_poker_task12()
        if self.task == 1:
            self.task_one()
        elif self.task == 2:
            self.task_two()

    def clicked_home_btn(self):
        """
        点击返回键后的函数
        """
        self.task = 0
        self.init_first_page()
        self.homeBtn.hide()
        try:
            self.nextBtn.deleteLater()
        except RuntimeError:
            pass
        except AttributeError:
            pass
        try:
            self.pokerWidget.deleteLater()
        except RuntimeError:
            pass
        except AttributeError:
            pass
        try:
            self.player1PokerWidget.deleteLater()
        except RuntimeError:
            pass
        except AttributeError:
            pass
        try:
            self.player2PokerWidget.deleteLater()
        except RuntimeError:
            pass
        except AttributeError:
            pass
        try:
            self.actionWidget.deleteLater()
        except RuntimeError:
            pass
        except AttributeError:
            pass
        try:
            self.passPlayLbl.deleteLater()
        except RuntimeError:
            pass
        except AttributeError:
            pass
        try:
            self.curPlayerLbl.deleteLater()
        except RuntimeError:
            pass
        except AttributeError:
            pass
        try:
            self.selectWidget.deleteLater()
        except RuntimeError:
            pass
        except AttributeError:
            pass
        try:
            self.confirmBtn.deleteLater()
        except RuntimeError:
            pass
        except AttributeError:
            pass

    def clicked_task_btn(self):
        """
        点击首页题目键后的函数
        """
        sender = self.sender()
        if sender.text() == "第一问":
            self.task = 1
            self.init_deal_page()
            self.homeBtn.show()
        elif sender.text() == "第二问":
            self.task = 2
            self.init_deal_page()
            self.homeBtn.show()
        elif sender.text() == "第三问":
            self.task = 3
            self.init_random_deal_page_task3()
            self.homeBtn.show()
    
    def confirm_poker_cnt(self):
        if not self.pokerCntInput.text():
            warning = QMessageBox()
            warning.warning(self, '警告', '未输入扑克牌数量', QMessageBox.standardButtons(warning).Yes)
        elif int(self.pokerCntInput.text()) > 54 or int(self.pokerCntInput.text()) < 1:
            warning = QMessageBox()
            warning.warning(self, '警告', '扑克牌数量需要在1~54之间', QMessageBox.standardButtons(warning).Yes)
        else:
            while self.centerLayout.count():
                child = self.centerLayout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            self.random_deal(int(self.pokerCntInput.text()))
            if self.task == 1:
                pass
            elif self.task == 2:
                pass

    def confirm_poker_cnt_task3(self):
        if not self.player1PokerCntInput.text() or not self.player2PokerCntInput.text():
            warning = QMessageBox()
            warning.warning(self, '警告', '未输入扑克牌数量', QMessageBox.standardButtons(warning).Yes)
        elif (int(self.player1PokerCntInput.text()) > 54 or int(self.player1PokerCntInput.text()) < 1 or
                int(self.player2PokerCntInput.text()) > 54 or int(self.player2PokerCntInput.text()) < 1):
            warning = QMessageBox()
            warning.warning(self, '警告', '扑克牌数量需要在1~54之间', QMessageBox.standardButtons(warning).Yes)
        else:
            while self.centerLayout.count():
                child = self.centerLayout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            self.random_deal_task3(int(self.player1PokerCntInput.text()), int(self.player2PokerCntInput.text()))

    def random_deal(self, pokerCnt):
        """
        随机发牌
        :param pokerCnt: 发牌的数量
        """
        self.pokerOrder = self.process.random_deal(pokerCnt)
        self.pokerImgs = [0 for _ in range(55)]
        for order in self.pokerOrder:
            pixmapLbl = QLabel(self)
            pixmapLbl.setFixedSize(102, 142)
            tmpPixmap = QPixmap("Cards\\" + str(order) + ".png")
            pixmapLbl.setScaledContents(True)
            pixmapLbl.setPixmap(tmpPixmap)
            self.pokerImgs[order] = pixmapLbl  # 扑克图片数组
        self.show_poker_task12()
        if self.task == 1:
            self.task_one()
        elif self.task == 2:
            self.task_two()

    def random_deal_task3(self, player1PokerCnt, player2PokerCnt):
        self.player1PokerOrder = self.process.deal_player1(player1PokerCnt)
        self.player1PokerImgs = [0 for _ in range(55)]
        for order in self.player1PokerOrder:
            pixmapLbl = QLabel(self)
            pixmapLbl.setFixedSize(102, 142)
            tmpPixmap = QPixmap("Cards\\" + str(order) + ".png")
            pixmapLbl.setScaledContents(True)
            pixmapLbl.setPixmap(tmpPixmap)
            self.player1PokerImgs[order] = pixmapLbl  # 扑克图片数组
        self.player2PokerOrder = self.process.deal_player2(player2PokerCnt)
        self.player2PokerImgs = [0 for _ in range(55)]
        for order in self.player2PokerOrder:
            pixmapLbl = QLabel(self)
            pixmapLbl.setFixedSize(102, 142)
            tmpPixmap = QPixmap("Cards\\" + str(order) + ".png")
            pixmapLbl.setScaledContents(True)
            pixmapLbl.setPixmap(tmpPixmap)
            self.player2PokerImgs[order] = pixmapLbl  # 扑克图片数组
        self.show_poker_task3()
        self.task_three()

    def show_poker_task12(self):
        """
        显示扑克牌，第一二问
        :param pos: 显示的位置，0表示下方，1表示上方
        """
        try:
            self.pokerWidget.deleteLater()
        except AttributeError:
            pass
        except RuntimeError:
            pass
        pokerLayout = QHBoxLayout(self)
        pokerLayout.addSpacing(80)
        for pixmapLbl in self.pokerImgs:
            if pixmapLbl:
                pokerLayout.addWidget(pixmapLbl)
                pokerLayout.addSpacing(-80)
        pokerLayout.addSpacing(80)
        self.pokerWidget = QWidget(self)
        self.pokerWidget.setMaximumWidth(self.width() - 160)
        self.pokerWidget.setLayout(pokerLayout)
        self.grid.addWidget(self.pokerWidget, 6, 3)

    def show_poker_task3(self):
        try:
            self.player1PokerWidget.deleteLater()
        except AttributeError:
            pass
        except RuntimeError:
            pass
        try:
            self.player2PokerWidget.deleteLater()
        except AttributeError:
            pass
        except RuntimeError:
            pass
        pokerLayout = QHBoxLayout(self)
        pokerLayout.addSpacing(80)
        for pixmapLbl in self.player1PokerImgs:
            if pixmapLbl:
                pokerLayout.addWidget(pixmapLbl)
                pokerLayout.addSpacing(-80)
        pokerLayout.addSpacing(80)
        self.player1PokerWidget = QWidget(self)
        self.player1PokerWidget.setMaximumWidth(self.width() - 160)
        self.player1PokerWidget.setLayout(pokerLayout)
        self.grid.addWidget(self.player1PokerWidget, 6, 3)

        pokerLayout = QHBoxLayout(self)
        pokerLayout.addSpacing(80)
        for pixmapLbl in self.player2PokerImgs:
            if pixmapLbl:
                pokerLayout.addWidget(pixmapLbl)
                pokerLayout.addSpacing(-80)
        pokerLayout.addSpacing(80)
        self.player2PokerWidget = QWidget(self)
        self.player2PokerWidget.setMaximumWidth(self.width() - 160)
        self.player2PokerWidget.setLayout(pokerLayout)
        self.grid.addWidget(self.player2PokerWidget, 0, 3)

    def task_one(self):
        """
        搜索最少的步骤的函数
        """
        self.nextBtn = QPushButton("下一步", self)
        self.nextBtn.clicked.connect(self.show_next_action_task_12)
        self.grid.addWidget(self.nextBtn, 3, 6)
        [self.step, self.path] = self.process.solve_without_score()

    def task_two(self):
        """
        搜索score最大的出牌步骤
        """
        self.nextBtn = QPushButton("下一步", self)
        self.nextBtn.clicked.connect(self.show_next_action_task_12)
        self.grid.addWidget(self.nextBtn, 3, 6)
        [self.score, self.step,  self.path] = self.process.solve_with_score()

    def task_three(self):
        """
        对战
        """
        self.nextBtn = QPushButton("下一步", self)
        self.nextBtn.clicked.connect(self.show_next_action_task3)
        self.grid.addWidget(self.nextBtn, 3, 6)
        self.curPlayerLbl = QLabel("玩家1出牌", self)
        self.curPlayerLbl.setStyleSheet("color:white")
        self.grid.addWidget(self.curPlayerLbl, 3, 0)
        [self.player1Actions, self.player2Actions, self.winner] = self.process.gaming()
        self.curPlayer = 1 # 当前的出牌玩家
        self.passPlayLbl = QLabel("不出", self)
        self.passPlayLbl.setStyleSheet("color:white")
        self.grid.addWidget(self.passPlayLbl, 3, 3)
        self.passPlayLbl.hide()

    def show_next_action_task_12(self):
        """
        显示第一二问的出牌步骤
        """
        if self.path:
            try:
                self.actionWidget.deleteLater()
            except AttributeError:
                pass
            except RuntimeError:
                pass
            action = self.path.pop(0)# 得到下一个步骤
            actionLayout = QHBoxLayout(self)
            actionLayout.addSpacing(80)
            for order in action:
                pixmapLbl = self.pokerImgs[order]
                self.pokerImgs[order] = 0
                actionLayout.addWidget(pixmapLbl)
                actionLayout.addSpacing(-80)
            actionLayout.addSpacing(80)
            self.actionWidget = QWidget(self)
            self.actionWidget.setMaximumWidth(self.width() - 160)
            self.actionWidget.setLayout(actionLayout)
            self.grid.addWidget(self.actionWidget, 3, 3)
            self.show_poker_task12()
        if not self.path:
            self.nextBtn.deleteLater()
            if self.task == 1:
                QMessageBox.about(self, "提示", "总共用了" + str(self.step) + "步")
            elif self.task == 2:
                QMessageBox.about(self, "提示", "总共用了" + str(self.step) + "步\nscore为: " + str(self.score))
            self.clicked_home_btn()

    def show_next_action_task3(self):
        """
        显示第一二问的出牌步骤
        """
        if self.player1Actions or self.player2Actions:
            try:
                self.actionWidget.deleteLater()
            except AttributeError:
                pass
            except RuntimeError:
                pass
            if self.curPlayer == 1:
                self.curPlayerLbl.setText("玩家1出牌")
                action = self.player1Actions.pop(0)# 得到下一个步骤
                if action: # 如果出牌的话
                    self.passPlayLbl.hide()
                    actionLayout = QHBoxLayout(self)
                    actionLayout.addSpacing(80)
                    for order in action:
                        pixmapLbl = self.player1PokerImgs[order]
                        self.player1PokerImgs[order] = 0
                        actionLayout.addWidget(pixmapLbl)
                        actionLayout.addSpacing(-80)
                    actionLayout.addSpacing(80)
                    self.actionWidget = QWidget(self)
                    self.actionWidget.setMaximumWidth(self.width() - 160)
                    self.actionWidget.setLayout(actionLayout)
                    self.grid.addWidget(self.actionWidget, 3, 3)
                    self.show_poker_task3()
                else: # 如果不出牌
                    self.actionWidget.hide()
                    self.passPlayLbl.show()
                self.curPlayer = 2
            elif self.curPlayer == 2:
                self.passPlayLbl.hide()
                self.curPlayerLbl.setText("玩家2出牌")
                action = self.player2Actions.pop(0)# 得到下一个步骤
                if action: # 如果出牌的话
                    actionLayout = QHBoxLayout(self)
                    actionLayout.addSpacing(80)
                    for order in action:
                        pixmapLbl = self.player2PokerImgs[order]
                        self.player2PokerImgs[order] = 0
                        actionLayout.addWidget(pixmapLbl)
                        actionLayout.addSpacing(-80)
                    actionLayout.addSpacing(80)
                    self.actionWidget = QWidget(self)
                    self.actionWidget.setMaximumWidth(self.width() - 160)
                    self.actionWidget.setLayout(actionLayout)
                    self.grid.addWidget(self.actionWidget, 3, 3)
                    self.show_poker_task3()
                else:  # 如果不出牌
                    self.actionWidget.hide()
                    self.passPlayLbl.show()
                self.curPlayer = 1
        if not (self.player1Actions or self.player2Actions):
            self.nextBtn.deleteLater()
            self.passPlayLbl.deleteLater()
            self.curPlayerLbl.deleteLater()
            QMessageBox.about(self, "提示", "玩家" + str(self.winner) + "获胜")
            self.clicked_home_btn()
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PokerWindow()
    window.show()
    sys.exit(app.exec())
