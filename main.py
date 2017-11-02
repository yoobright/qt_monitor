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