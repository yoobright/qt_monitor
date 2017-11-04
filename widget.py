# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWinExtras import QtWin

from utils.log import logger
from ui import *


DEFAULT_PERSON_IMG = 'images/person.png'


class ToolBar(QToolBar):
    def __init__(self, title):
        super(ToolBar, self).__init__(title)
        layout = self.layout()
        m = (0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setContentsMargins(*m)
        self.setContentsMargins(*m)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

    def addAction(self, action):
        if isinstance(action, QWidgetAction):
            return super(ToolBar, self).addAction(action)
        btn = QToolButton()
        btn.setDefaultAction(action)
        btn.setToolButtonStyle(self.toolButtonStyle())
        self.addWidget(btn)


class struct(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def newIcon(icon):
    return QIcon(':/' + icon)


def addActions(widget, actions):
    for action in actions:
        if action is None:
            widget.addSeparator()
        elif isinstance(action, QMenu):
            widget.addMenu(action)
        else:
            widget.addAction(action)


def newAction(parent, text, slot=None, shortcut=None, icon=None,
              tip=None, checkable=False, enabled=True):
    """Create a new action and assign callbacks, shortcuts, etc."""
    a = QAction(text, parent)
    if icon is not None:
        a.setIcon(newIcon(icon))
    if shortcut is not None:
        if isinstance(shortcut, (list, tuple)):
            a.setShortcuts(shortcut)
        else:
            a.setShortcut(shortcut)
    if tip is not None:
        a.setToolTip(tip)
        a.setStatusTip(tip)
    if slot is not None:
        a.triggered.connect(slot)
    if checkable:
        a.setCheckable(True)
    a.setEnabled(enabled)
    return a


def centreLayoutWarp(widget):
    layout = QHBoxLayout()
    layout.addWidget(widget, 0, Qt.AlignHCenter)
    return layout


def subHLayout(add_list):
    layout = QHBoxLayout()
    for item in add_list:
        if isinstance(item, QWidget):
            layout.addWidget(item)
        elif item == 'stretch':
            layout.addStretch()
    return layout


class WindowMixin(object):
    def menu(self, title, actions=None):
        menu = self.menuBar().addMenu(title)
        if actions:
            addActions(menu, actions)
        return menu

    def toolbar(self, title, actions=None):
        toolbar = ToolBar(title)
        toolbar.setObjectName(u'%sToolBar' % title)
        # toolbar.setOrientation(Qt.Vertical)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        if actions:
            addActions(toolbar, actions)
        self.addToolBar(Qt.BottomToolBarArea, toolbar)
        return toolbar


class ImageWidget(QWidget):
    def __init__(self, pixmap=None, parent=None, min_size=QSize(128, 128),
                 margin=5):
        super(ImageWidget, self).__init__(parent)
        self.default_pixmap = QPixmap(DEFAULT_PERSON_IMG)
        self.pixmap = pixmap
        self.imageLabel = QLabel()
        self.imageLabel.setMinimumSize(min_size)
        self.imageLabel.setMaximumSize(QSize(200, 200))
        self.infoLabel = QLabel('test')
        self.infoLabel.setMaximumWidth(200)
        self.infoLabel.setMargin(2)
        self.infoLabel.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.setContentsMargins(margin, margin, margin, margin)
        layout.addStretch()
        layout.addWidget(self.imageLabel)
        layout.addWidget(self.infoLabel)
        layout.addStretch()
        self.setLayout(layout)
        self.setStyleSheet("border:1px solid")

    def resizeEvent(self, event):
        self.updateImage()
        QWidget.resizeEvent(self, event)

    def updateImage(self):
        if self.pixmap:
            show_map = self.pixmap.copy()
        else:
            show_map = self.default_pixmap.copy()
        size = self.imageLabel.width() - 2
        show_map = show_map.scaledToWidth(size,
                                          Qt.SmoothTransformation)
        self.imageLabel.setPixmap(show_map)


class capFrame(QAbstractScrollArea):
    def __init__(self, parent=None):
        super(capFrame, self).__init__(parent)

        self.contentsWidget = QListWidget()
        self.contentsWidget.setResizeMode(QListView.Adjust)
        # self.contentsWidget.setSizeAdjustPolicy(QListWidget.AdjustToContents)
        self.contentsWidget.setViewMode(QListView.IconMode)
        self.contentsWidget.setIconSize(QSize(128, 128))
        self.contentsWidget.setMovement(QListView.Static)
        self.contentsWidget.setMaximumWidth(800)
        self.contentsWidget.setSpacing(12)
        self.updateState()
        horizontalLayout = QHBoxLayout()
        horizontalLayout.setContentsMargins(4, 4, 4, 4)
        horizontalLayout.addWidget(self.contentsWidget)
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(horizontalLayout)
        self.setLayout(mainLayout)

    def updateState(self):
        num = 10
        for i in range(num):
            item = QListWidgetItem(self.contentsWidget)
            item.setSizeHint(QSize(160, 190))
            # configButton.set
            item.setIcon(QIcon('images/person.png'))
            item.setText("person-{}".format(i))
            item.setTextAlignment(Qt.AlignHCenter)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)


    #QListWidget current 改变时触发
    def changePage(self, current, previous):
        print(self.contentsWidget.row(current))


class DetectTable(QTableWidget):
    def __init__(self, parent=None):
        super(DetectTable, self).__init__(parent)
        self.setupUi()

    def setupUi(self):
        # self.setMinimumHeight(340)
        # self.setMaximumWidth(200)
        self.setColumnCount(4)
        self.setRowCount(10)
        self.verticalHeader().setVisible(False)
        self.setHorizontalHeaderLabels(['报警时间', '设备名称',
                                        '相似度', '姓名'])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.selectRow(0)


class CompareWidget(QWidget):
    def __init__(self, parent=None):
        super(CompareWidget, self).__init__(parent)
        layout = QHBoxLayout()
        self.cap_image = ImageWidget(margin=2)
        self.cap_image.infoLabel.setText('抓拍图象')
        self.cmp_image = ImageWidget(margin=2)
        self.similarityLabel = QLabel('0%')
        self.similarityLabel.setMinimumWidth(50)
        self.similarityLabel.setAlignment(Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.cap_image)
        layout.addWidget(self.similarityLabel)
        layout.addWidget(self.cmp_image)
        layout.addStretch()
        self.setLayout(layout)

    def setupUi(self):
        pass


class BottomWidget(QAbstractScrollArea):
    def __init__(self, parent=None):
        super(BottomWidget, self).__init__(parent)
        layout = QGridLayout()
        self.compareWidget = CompareWidget()
        self.detectTable = DetectTable()
        layout.addWidget(self.compareWidget, 0, 0)
        layout.addWidget(self.detectTable, 0, 1)
        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(1, 3)

        self.setLayout(layout)

    def setupUi(self):
        pass


class MainWindow(QMainWindow, WindowMixin):
    def __init__(self, parent=None, debug=False):
        QMainWindow.__init__(self, parent)
        self.setupUi()
        self.setAttribute(Qt.WA_TranslucentBackground)
        QtWin.enableBlurBehindWindow(self)
        QtWin.extendFrameIntoClientArea(self, -1, -1, -1, -1)
        self.videoTimer = QTimer()
        self.videoTimer.setInterval(40)
        self.start_timer()

        self.videoTimer.timeout.connect(self.updateCamera)

    def setupUi(self):

        # self.centralWidget = QWidget(MainWindow)
        # self.button = QPushButton(MainWindow)

        self.bottomWidget = BottomWidget()
        self.leftWidget = QAbstractScrollArea()
        self.rightWidget = capFrame()

        self.topSplitter = QSplitter(self)
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

        self.setWindowTitle('test')
        self.setMinimumSize(960, 720)
        self.resize(960, 720)
        self.setCentralWidget(self.topSplitter)

    def start_timer(self):
        logger.debug('{}: start timer'.format(self.__class__))
        self.videoTimer.start()

    def stop_timer(self):
        logger.debug('{}: stop timer'.format(self.__class__))
        self.videoTimer.stop()

    def updateCamera(self):
        pass

