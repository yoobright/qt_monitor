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

import pyqt5_style
from utils.log import logger
from utils.utils import np2qimage
from widget import MainWindow

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

if sys.version_info[0] >= 3:
    from io import StringIO
else:
    from StringIO import StringIO


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

def getPalette():
    darkPalette = QPalette()
    darkPalette.setColor(QPalette.Window,QColor(53,53,53))
    darkPalette.setColor(QPalette.WindowText,Qt.white)
    darkPalette.setColor(QPalette.Disabled,QPalette.WindowText,QColor(127,127,127))
    darkPalette.setColor(QPalette.Base,QColor(42,42,42))
    darkPalette.setColor(QPalette.AlternateBase,QColor(66,66,66))
    darkPalette.setColor(QPalette.ToolTipBase,Qt.white)
    darkPalette.setColor(QPalette.ToolTipText,Qt.white)
    darkPalette.setColor(QPalette.Text,Qt.white)
    darkPalette.setColor(QPalette.Disabled,QPalette.Text,QColor(127,127,127))
    darkPalette.setColor(QPalette.Dark,QColor(35,35,35))
    darkPalette.setColor(QPalette.Shadow,QColor(20,20,20))
    darkPalette.setColor(QPalette.Button,QColor(53,53,53))
    darkPalette.setColor(QPalette.ButtonText,Qt.white)
    darkPalette.setColor(QPalette.Disabled,QPalette.ButtonText,QColor(127,127,127))
    darkPalette.setColor(QPalette.BrightText,Qt.red)
    darkPalette.setColor(QPalette.Link,QColor(42,130,218))
    darkPalette.setColor(QPalette.Highlight,QColor(42,130,218))
    darkPalette.setColor(QPalette.Disabled,QPalette.Highlight,QColor(80,80,80))
    darkPalette.setColor(QPalette.HighlightedText,Qt.white)
    darkPalette.setColor(QPalette.Disabled,QPalette.HighlightedText,QColor(127,127,127))

    return darkPalette

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setPalette(getPalette())
    qss_file = QFile(":darkstyle/darkstyle.qss")
    qss_file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(qss_file)
    app.setStyleSheet(stream.readAll())
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