# -*- coding:utf-8 -*-

from functools import wraps
from time import time

import numpy as np
from numpy.linalg import norm
import cv2

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from utils.log import logger


def singleton(class_):
    instances = {}

    def get_instance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return get_instance


def fn_timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time()
        result = function(*args, **kwargs)
        t1 = time()
        logger.debug("time running {}: {:.2f}ms".format(
            function.__name__, (t1 - t0) * 1000)
        )
        return result

    return function_timer


def np2qimage(img, mode=None):
    if len(img.shape) != 3:
        raise ValueError("np2QImage can only convert 3D arrays")
    if img.shape[2] not in (3, 4):
        raise ValueError(
            "rgb2QImage can expects the last dimension to contain exactly "
            "three or four channels")
    height, width, channels = img.shape
    strides = img.strides[0]
    if mode == 'bgr':
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    if channels == 3:
        qim = QImage(img.data, width, height, strides,
                     QImage.Format_RGB888)
        return qim
    elif channels == 4:
        qim = QImage(img.data, width, height, strides,
                     QImage.Format_RGB888)
        return qim
    return None


def qimage2np(qimage, mode='bgr'):
    qimage = qimage.convertToFormat(QImage.Format_RGB888)
    width = qimage.width()
    height = qimage.height()
    ptr = qimage.bits()
    ptr.setsize(qimage.byteCount())
    img_np = np.array(ptr).reshape((height, width, 3))
    if mode == 'bgr':
        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    return img_np

def convertQImageToMat(incomingImage):
    ''' Converts a QImage into an opencv MAT format '''
    incomingImage = incomingImage.convertToFormat(4)
    width = incomingImage.width()
    height = incomingImage.height()
    ptr = incomingImage.bits()
    ptr.setsize(incomingImage.byteCount())
    arr = np.array(ptr).reshape(height, width, 4)

def get_similarity(x, y):
    return np.dot(x, y) / (norm(x) * norm(y))
