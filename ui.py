# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow: QMainWindow):

        # self.centralWidget = QWidget(MainWindow)
        # self.button = QPushButton(MainWindow)

        self.bottomWidget = QAbstractScrollArea()
        self.leftWidget = QAbstractScrollArea()
        self.rightWidget = QAbstractScrollArea()

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


