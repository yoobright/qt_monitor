# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class capFrame(QAbstractScrollArea):
    def __init__(self, parent=None):
        super(capFrame, self).__init__(parent)

        self.contentsWidget = QListWidget()
        self.contentsWidget.setResizeMode(QListView.Adjust)
        # self.contentsWidget.setSizeAdjustPolicy(QListWidget.AdjustToContents)
        self.contentsWidget.setViewMode(QListView.IconMode)
        self.contentsWidget.setIconSize(QSize(128, 128))  #Icon 大小
        self.contentsWidget.setMovement(QListView.Static)  #Listview显示状态
        self.contentsWidget.setMaximumWidth(800)  # 最大宽度
        self.contentsWidget.setSpacing(12)  # 间距大小
        self.createIcons()
        horizontalLayout = QHBoxLayout()
        horizontalLayout.addWidget(self.contentsWidget)
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(horizontalLayout)
        self.setLayout(mainLayout)

    def createIcons(self):
        num = 10
        for i in range(num):
            item = QListWidgetItem(self.contentsWidget)
            item.setSizeHint(QSize(160, 200))
            # configButton.set
            item.setIcon(QIcon('images/person.png'))
            item.setText("person-{}".format(i))
            item.setTextAlignment(Qt.AlignHCenter)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)


    #QListWidget current 改变时触发
    def changePage(self, current, previous):
        print(self.contentsWidget.row(current))

class Ui_MainWindow(object):
    def setupUi(self, MainWindow: QMainWindow):

        # self.centralWidget = QWidget(MainWindow)
        # self.button = QPushButton(MainWindow)

        self.bottomWidget = QAbstractScrollArea()
        self.leftWidget = QAbstractScrollArea()
        self.rightWidget = capFrame()

        self.topSplitter = QSplitter(MainWindow)
        self.topSplitter.setOrientation(Qt.Vertical)

        self.secSplitter = QSplitter()
        self.secSplitter.setOrientation(Qt.Horizontal)
        self.secSplitter.addWidget(self.leftWidget)
        self.secSplitter.addWidget(self.rightWidget)
        self.topSplitter.addWidget(self.secSplitter)
        self.topSplitter.addWidget(self.bottomWidget)

        self.secSplitter.setStretchFactor(0, 4)
        self.secSplitter.setStretchFactor(1, 3)
        self.topSplitter.setStretchFactor(0, 5)
        self.topSplitter.setStretchFactor(1, 3)
        MainWindow.setWindowTitle('test')
        MainWindow.setMinimumSize(800, 600)
        MainWindow.resize(960, 720)
        MainWindow.setCentralWidget(self.topSplitter)


