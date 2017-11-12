# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import queue
import threading

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWinExtras import QtWin

import backend
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


class ImageWidget(QFrame):
    def __init__(self, pixmap=None, parent=None, min_size=QSize(128, 128),
                 margin=5):
        super(ImageWidget, self).__init__(parent)
        self.default_pixmap = QPixmap(DEFAULT_PERSON_IMG)
        self.pixmap = pixmap
        self.imageLabel = QLabel()
        self.imageLabel.setMinimumSize(min_size)
        self.imageLabel.setMaximumSize(QSize(180, 180))
        self.infoLabel = QLabel('test')
        self.infoLabel.setMaximumWidth(180)
        self.infoLabel.setMinimumHeight(30)
        self.infoLabel.setMaximumHeight(40)
        self.infoLabel.setMargin(2)
        self.infoLabel.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.setContentsMargins(margin, margin, margin, margin)
        layout.addStretch()
        layout.addWidget(self.imageLabel)
        layout.addWidget(self.infoLabel)
        self.setContentsMargins(margin, margin, margin, margin)
        layout.addStretch()
        self.setLayout(layout)
        self.setMinimumHeight(150)
        self.setMaximumHeight(220)
        # self.updateImage()

        self.setStyleSheet("border:1px solid #3daee9")

    # def paintEvent(self, event):
    #     # self.updateImage()
    #     super(ImageWidget, self).paintEvent(event)

    # def resizeMax(self):
    #     self.imageLabel.resize(200, 200)
    #     self.infoLabel.resize(200, 30)

    def updateImage(self, pixmap=None):
        if pixmap is not None:
            self.pixmap = pixmap

        if self.pixmap:
            show_map = self.pixmap.copy()
        else:
            show_map = self.default_pixmap.copy()
        size = self.imageLabel.width() - 2
        show_map = show_map.scaledToWidth(size,
                                          Qt.SmoothTransformation)
        self.imageLabel.setPixmap(show_map)


class VideoWidget(QFrame):
    def __init__(self, parent=None, rightClickCallback=None):
        super(VideoWidget, self).__init__(parent)
        self.setupUi()
        self.rightClickCallback = rightClickCallback
        self.capture = backend.VideoCapture()
        # self.thread = backend.VideoThread(self)
        self.frame = queue.Queue()
        self.videoTimer = QTimer()
        self.videoTimer.setInterval(30)

        # self.thread.cap_frame.connect(self.setFrame)
        self.videoTimer.timeout.connect(self.timerUpdate)
        self.start_timer()
        # self.thread.start()

    def setupUi(self):
        self.default_pixmap = QPixmap('images/video.png')
        self.pixmap = None
        self.imageLabel = QLabel()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.imageLabel)
        self.imageLabel.setMinimumSize(QSize(200, 200))
        self.imageLabel.setPixmap(self.default_pixmap)
        self.setLayout(layout)
        self.setStyleSheet(
            '''
            QLabel {
            border: 2px solid rgb(0, 0, 0, 0);
            }
                    
            QLabel:hover {
            border: 2px solid rgb(96, 95, 95, 255);
            }
            '''
        )

    def resizeEvent(self, event):
        self.updatePixmap()
        super(VideoWidget, self).resizeEvent(event)

    def start_timer(self):
        self.videoTimer.start()

    def stop_timer(self):
        self.videoTimer.stop()

    def updatePixmap(self):
        if not self.frame.empty():
            self.pixmap = QPixmap(self.frame.get())

        if self.pixmap:
            show_pixmap = self.pixmap.copy()
        else:
            show_pixmap = self.default_pixmap.copy()

        show_pixmap = show_pixmap.scaledToWidth(
            self.imageLabel.width(),
            Qt.SmoothTransformation)
        self.imageLabel.setPixmap(show_pixmap)

    def timerUpdate(self):
        im = self.capture.get_frame()
        if not im.isNull():
            self.pixmap = QPixmap(im)
        self.updatePixmap()
    # def setFrame(self, image):
    #     # print('set')
    #     if self.frame.empty():
    #         self.frame.put(image)
    #         self.update()

    # def terminate(self, event):
    #     self.thread.terminate()


class VideoMonitor(QAbstractScrollArea):
    title = ' 实时监控'

    def __init__(self, parent=None):
        super(VideoMonitor, self).__init__(parent)
        self.setupUi()

    def genTitle(self):
        label = QLabel(self.title)
        label.setMinimumHeight(25)
        label.setMaximumHeight(25)
        label.setStyleSheet(
            '''
            font: bold;
            background-color:  #3daee9
            '''
        )
        return label


    def setupUi(self):
        layout = QGridLayout()
        # layout.setHorizontalSpacing(1)
        # layout.setVerticalSpacing(1)
        self.video_1 = VideoWidget(self)
        self.video_2 = VideoWidget(self)
        layout.addWidget(self.genTitle(), 0, 0)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        layout.addWidget(self.video_1, 1, 0)
        layout.addWidget(self.video_2, 2, 0)
        self.setLayout(layout)
        self.setMinimumWidth(350)
        # self.setContentsMargins(2, 2, 2, 2)


class capFrame(QAbstractScrollArea):
    show_top = 50
    title = ' 人脸抓拍'

    def __init__(self, parent=None):
        super(capFrame, self).__init__(parent)

        self.contentsWidget = QListWidget()
        self.contentsWidget.setResizeMode(QListView.Adjust)
        # self.contentsWidget.setSizeAdjustPolicy(QListWidget.AdjustToContents)
        self.contentsWidget.setViewMode(QListView.IconMode)
        self.contentsWidget.setIconSize(QSize(120, 120))
        self.contentsWidget.setMovement(QListView.Static)
        # self.contentsWidget.setMaximumWidth(800)
        self.contentsWidget.setSpacing(12)
        layout = QGridLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(self.genTitle(), 0, 0)
        layout.addWidget(self.contentsWidget, 1, 0)

        self.setLayout(layout)

    def genTitle(self):
        label = QLabel(self.title)
        label.setMinimumHeight(25)
        label.setMaximumHeight(25)
        label.setStyleSheet(
            '''
            font: bold;
            background-color:  #3daee9
            '''
        )
        return label

    def updateState(self, data=None):
        data = backend.get_capture()
        self.contentsWidget.clear()
        for d in data[:self.show_top]:
            item = QListWidgetItem(self.contentsWidget)
            item.setSizeHint(QSize(150, 190))
            # configButton.set
            item.setIcon(QIcon(d.pixmap))
            item.setText('{}'.format(d.date))
            item.setTextAlignment(Qt.AlignHCenter)
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)


class SimilarityBar(QProgressBar):
    _DEFAULT_STYLE = '''
    * {font-size: 10pt;}
    QProgressBar {
    text-align: left;
    height: 20px;  
    }      
    QProgressBar::chunk {
    background-color: rgb(213, 78, 83, 180);
    width: 1px;
    }           
    '''
    _LOW_STYLE = '''
    * {font-size: 10pt;}
    QProgressBar {
    text-align: left;
    height: 20px;  
    }      
    QProgressBar::chunk {
    background-color: rgb(231, 197, 71, 180);
    width: 1px;
    }           
    '''

    def __init__(self, parent=None, max_width=60):
        QProgressBar.__init__(self, parent)
        self.setRange(0, 100)
        self.setStyleSheet(self._DEFAULT_STYLE)
        self.setMaximumWidth(max_width)
        self.setMaximumHeight(22)


class DetectTable(QTableWidget):
    show_top = 50

    def __init__(self, parent=None):
        super(DetectTable, self).__init__(parent)
        self.setupUi()

    def setupUi(self):
        # self.setMinimumHeight(340)
        # self.setMaximumWidth(200)
        self.setColumnCount(4)
        self.setRowCount(self.show_top)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setHorizontalHeaderLabels(['报警时间', '设备名称',
                                        '相似度', '姓名'])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.selectRow(0)

    def genSimilarityBar(self, value):
        assert 0 <= value <= 100, 'value must between 0 and 100'
        widget = QWidget()
        layout = QHBoxLayout()
        bar = SimilarityBar()
        bar.setValue(value)
        if value < 75:
            bar.setStyleSheet(bar._LOW_STYLE)
        layout.addWidget(bar)
        layout.addStretch()
        layout.setContentsMargins(4, 0, 0, 0)
        widget.setLayout(layout)
        widget.setStyleSheet(
            '''
            font: bold;
            background: rgb(0, 0, 0, 0)
            '''
        )
        return widget

    def updateState(self, data=None):
        logger.debug('update DetectTable state')
        selected_row = None
        self.setHorizontalHeaderLabels(['报警时间', '设备名称',
                                        '相似度', '姓名'])
        for i, d in enumerate(data[:self.show_top]):
            self.setItem(i, 0, QTableWidgetItem(d.date_time))
            self.setItem(i, 1, QTableWidgetItem(d.cam_id))
            self.setCellWidget(i, 2, self.genSimilarityBar(d.similarity))
            self.setItem(i, 3, QTableWidgetItem(d.cmp_id))


class CompareWidget(QFrame):
    _SML_DEFAULT_STYLE = '''
    font: bold;
    color: rgb(213, 78, 83);
    '''
    _SML_LOW_STYLE = '''
    font: bold;
    color: rgb(231, 197, 71);
    '''

    def __init__(self, parent=None):
        super(CompareWidget, self).__init__(parent)
        self.setupUi()
        self.centralWidget.hide()

    def setupUi(self):
        self.setObjectName('top')
        layout = QGridLayout()
        self.centralWidget = QFrame()
        self.centralWidget.setMaximumWidth(480)
        self.cap_image = ImageWidget(margin=2)
        self.cap_image.infoLabel.setText('抓拍图象')
        self.cmp_image = ImageWidget(margin=2)
        self.similarityLabel = QLabel()
        self.updateSimilarity(0)
        self.similarityLabel.setMinimumWidth(50)
        self.similarityLabel.setMinimumWidth(50)
        self.similarityLabel.setAlignment(Qt.AlignCenter)
        # layout.setStretchFactor(self.similarityLabel, 1)
        # layout.setStretchFactor(self.cap_image, 2)
        # layout.setStretchFactor(self.cmp_image, 2)
        # layout.addStretch()
        layout.addWidget(self.cap_image, 0, 0)
        layout.addWidget(self.similarityLabel, 0, 1)
        layout.addWidget(self.cmp_image, 0, 2)
        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 2)
        # layout.addStretch()
        self.centralWidget.setLayout(layout)
        # self.centralWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        top_layout = QGridLayout()
        top_layout.addWidget(self.centralWidget)
        self.setLayout(top_layout)

        self.setStyleSheet(
            '''
            #top {
            background-color: rgb(35, 38, 41);
            border: 2px solid rgb(118, 121, 124);
            }
            QLabel[tag='true'] {
            font: 22px;
            }
            '''
        )

    def updateSimilarity(self, value):
        self.similarityLabel.setText('{0:.0f}%'.format(value))
        if value < 75:
            self.similarityLabel.setStyleSheet(self._SML_LOW_STYLE)
        else:
            self.similarityLabel.setStyleSheet(self._SML_DEFAULT_STYLE)


    def resizeEvent(self, event):
        if self.width() > 500:
            self.setContentsMargins(30, 30, 30, 30)
            self.similarityLabel.setProperty('tag', True)
            self.similarityLabel.setStyle(self.similarityLabel.style())
        else:
            self.setContentsMargins(10, 10, 10, 10)
            self.similarityLabel.setProperty('tag', False)
            self.similarityLabel.setStyle(self.similarityLabel.style())

        super(CompareWidget, self).resizeEvent(event)
        self.cap_image.updateImage()
        self.cmp_image.updateImage()


    def updateState(self, data):
        logger.debug('update CompareWidget state')
        self.cap_image.updateImage(data.cap_pixmap)
        self.cmp_image.updateImage(data.cmp_pixmap)
        self.cmp_image.infoLabel.setText(data.cmp_id)
        self.updateSimilarity(data.similarity)


class BottomWidget(QAbstractScrollArea):
    title = ' 黑名单报警'

    def __init__(self, parent=None):
        super(BottomWidget, self).__init__(parent)
        self.setupUi()
        self.data = None
        self.detectTable.selectionModel().selectionChanged.connect(
            self.selectChangeSlot)

    def genTitle(self):
        label = QLabel(self.title)
        label.setMinimumHeight(25)
        label.setMaximumHeight(25)
        label.setStyleSheet(
            '''
            font: bold;
            background-color:  #3daee9
            '''
        )
        return label

    def setupUi(self):
        layout = QGridLayout()
        self.compareWidget = CompareWidget()
        self.detectTable = DetectTable()
        layout.addWidget(self.genTitle(), 0, 0, 1, 2)
        layout.addWidget(self.compareWidget, 1, 0)
        layout.addWidget(self.detectTable, 1, 1)
        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(1, 3)
        layout.setContentsMargins(4, 4, 4, 4)
        self.setLayout(layout)

    def selectChangeSlot(self, selected):
        if self.data is None:
            return
        if len(selected.indexes()) > 0:
            index = selected.indexes()[0].row()
            if index < len(self.data):
                self.compareWidget.updateState(self.data[index])
                self.compareWidget.centralWidget.show()
            else:
                self.compareWidget.centralWidget.hide()

    def updateState(self, data=None):
        logger.debug('update BottomWidget state')
        if data is not None:
            self.data = data
        if self.data is None:
            return
        self.detectTable.updateState(self.data)
        select_index = None
        try:
            select_index = self.detectTable.selectedIndexes()[0].row()
        except IndexError as ex:
            logger.debug('select index except: {}'.format(ex))
            return
        if select_index is not None and select_index < len(self.data):
            self.compareWidget.centralWidget.show()
            self.compareWidget.updateState(self.data[select_index])
        else:
            self.compareWidget.centralWidget.hide()
        # self.detectTable.updateState()


class MainWindow(QMainWindow, WindowMixin):
    def __init__(self, parent=None, debug=False):
        QMainWindow.__init__(self, parent)
        self.setupUi()
        self.setAttribute(Qt.WA_TranslucentBackground)
        QtWin.enableBlurBehindWindow(self)
        QtWin.extendFrameIntoClientArea(self, -1, -1, -1, -1)
        self.infoTimer = QTimer()
        self.infoTimer.setInterval(2000)
        self.start_timer()

        self.infoTimer.timeout.connect(self.updateInfo)

    def setupUi(self):

        # self.centralWidget = QWidget(MainWindow)
        # self.button = QPushButton(MainWindow)

        self.bottomWidget = BottomWidget(self)
        self.leftWidget = VideoMonitor(self)
        self.rightWidget = capFrame(self)

        self.topSplitter = QSplitter(self)
        self.topSplitter.setOrientation(Qt.Vertical)

        self.secSplitter = QSplitter()
        self.secSplitter.setOrientation(Qt.Horizontal)
        self.secSplitter.addWidget(self.leftWidget)
        self.secSplitter.addWidget(self.rightWidget)
        # self.secSplitter.set
        self.topSplitter.addWidget(self.secSplitter)
        self.topSplitter.addWidget(self.bottomWidget)

        self.secSplitter.setStretchFactor(0, 4)
        self.secSplitter.setStretchFactor(1, 3)
        self.topSplitter.setStretchFactor(0, 5)
        self.topSplitter.setStretchFactor(1, 3)

        self.setWindowTitle('Monitor')
        self.setMinimumSize(960, 720)
        self.resize(960, 720)
        self.topSplitter.setContentsMargins(15, 15, 15, 15)
        self.setCentralWidget(self.topSplitter)

    def start_timer(self):
        logger.debug('{}: start timer'.format(self.__class__))
        self.infoTimer.start()

    def stop_timer(self):
        logger.debug('{}: stop timer'.format(self.__class__))
        self.infoTimer.stop()

    def updateInfo(self):
        logger.debug('update main window info')
        cap_data = backend.get_capture()
        if cap_data:
            self.rightWidget.updateState(cap_data)
        alert_data = backend.get_alert()
        if alert_data:
            self.bottomWidget.updateState(alert_data)
