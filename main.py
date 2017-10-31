# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import sys
import os
import time
import queue
import cv2
import traceback
import logging
import pytz
from datetime import datetime

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from utils.log import logger
from utils.utils import np2qimage

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

if sys.version_info[0] >= 3:
    from io import StringIO
else:
    from StringIO import StringIO


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


class Ui_MainWindow(object):
    def setupUi(self, MainWindow: QMainWindow):
        MainWindow.setWindowTitle('test')
        MainWindow.setMinimumSize(800, 600)
        MainWindow.resize(800, 600)
        self.button = QPushButton(MainWindow)


class MainWindow(QMainWindow, WindowMixin):
    def __init__(self, parent=None, debug=False):
        QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.button.setText('hello')

        self.videoTimer = QTimer()
        self.videoTimer.setInterval(40)
        self.start_timer()

        self.videoTimer.timeout.connect(self.updateCamera)

    def start_timer(self):
        logger.debug('{}: start timer'.format(self.__class__))
        self.videoTimer.start()

    def stop_timer(self):
        logger.debug('{}: stop timer'.format(self.__class__))
        self.videoTimer.stop()

    def updateCamera(self):
        pass



def excepthook(excType, excValue, tracebackobj):
    """
    Global function to catch unhandled exceptions.

    @param excType exception type
    @param excValue exception value
    @param tracebackobj traceback object
    """
    separator = '-' * 80
    logFile = os.path.join(APP_ROOT, "simple.log")
    notice = \
        """An unhandled exception occurred. Please report the problem\n"""\
        """using the error reporting dialog or via email to <%s>.\n"""\
        """A log has been written to "%s".\n\nError information:\n""" % \
        ("yourmail at server.com", logFile)
    versionInfo = "0.0.1"
    timeString = time.strftime("%Y-%m-%d, %H:%M:%S")

    tbinfofile = StringIO()
    traceback.print_tb(tracebackobj, None, tbinfofile)
    tbinfofile.seek(0)
    tbinfo = tbinfofile.read()
    errmsg = '%s: \n%s' % (str(excType), str(excValue))
    sections = [separator, timeString, separator, errmsg, separator, tbinfo]
    msg = '\n'.join(sections)
    try:
        with open(logFile, "w") as f:
            f.write(msg)
            f.write(versionInfo)
    except IOError:
        pass
    errorbox = QMessageBox()
    errorbox.setText(str(notice)+str(msg)+str(versionInfo))
    errorbox.setWindowTitle(' An Unhandled Exception Occurred')
    errorbox.exec_()

sys.excepthook = excepthook

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        app.setFont(QFont('微软雅黑'))
    except Exception:
        print('load font failed')
    debug = 'debug' in sys.argv
    if debug:
        logger.setLevel(logging.DEBUG)
    logger.info('start main app ...')
    myapp = MainWindow(debug=debug)
    myapp.show()
    sys.exit(app.exec_())