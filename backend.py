# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
from time import time

import cv2

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from utils.utils import *


def load_img(image_path):
    pixmap = QPixmap(image_path)
    if pixmap.isNull():
        pixmap = QPixmap('images/person.png')
    return pixmap


class CaptureData(object):
    def __init__(self, date, image_path):
        self.date = date
        self.pixmap = load_img(image_path)


def get_capture():
    data_list = []
    for i in range(10):
        now = datetime.datetime.now()
        date = '{}\n{}'.format(now.strftime('%Y-%m-%d'),
                               now.strftime('%H:%M:%S'))
        data = CaptureData(
            date=date,
            image_path='person.png'
        )
        data_list.append(data)

    if len(data_list) == 0:
        return None
    return data_list


class AlertData(object):
    def __init__(self, cmp_id, cam_id, date_time, similarity,
                 cap_image_path, cmp_image_path):
        self.cmp_id = cmp_id
        self.cam_id = cam_id
        self.date_time = date_time
        self.similarity = similarity
        self.cap_pixmap = load_img(cap_image_path)
        self.cmp_pixmap = load_img(cmp_image_path)


def get_alert():
    data_list = []
    for i in range(10):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = AlertData(
            cmp_id='person_{}'.format(i),
            cam_id='cam_{}'.format(i),
            date_time=now,
            similarity=float(100-i*10),
            cap_image_path='cap.png',
            cmp_image_path='cmp.png'
        )
        data_list.append(data)
    if len(data_list) == 0:
        return None
    return data_list


class VideoCapture(object):
    def __init__(self, id=0):
        self.interval = 40
        self.cap = cv2.VideoCapture(id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

    def get_frame(self):
        b, frame = self.cap.read()
        im = np2qimage(frame, mode='bgr')
        return im


class VideoThread(QThread):
    start_timer = pyqtSignal()
    pixmap_changed = pyqtSignal(QPixmap)

    def __init__(self, parent, callback, id=0):
        super(VideoThread, self).__init__(parent)
        self.interval = 20
        self.callback = callback
        self.cap = cv2.VideoCapture('rtsp://admin:pdl111111@10.0.119.101//Streaming/Channels/1')
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
        # self.thread.cap_frame.connect(self.setFrame)
        self.timer = QTimer()
        self.count = 0
        self.start_timer.connect(self.slot_timer_start)
        self.timer.timeout.connect(self.get_frame)
        self.start_tag = time()

    @pyqtSlot()
    def get_frame(self):
        self.count += 1
        b, frame = self.cap.read()
        if self.count == 10:
            self.count = 0
            print(10 / (time() - self.start_tag))
            self.start_tag = time()
        if frame is not None:
            im = np2qimage(frame, mode='bgr')
            self.callback(QPixmap(im))

    @pyqtSlot()
    def slot_timer_start(self):
        print('slot')
        self.timer.start(self.interval)

    def run(self):
        print('run')
        self.start_timer.emit()
        self.exec_()

    def setInterval(self, value):
        self.interval = value

