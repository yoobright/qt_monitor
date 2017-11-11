# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
from PyQt5.QtGui import QPixmap
def updateVideo():
    pass


def load_img(image_path):
    pixmap = QPixmap(image_path)
    if pixmap.isNull():
        pixmap = QPixmap('images/person.png')
    return pixmap


class CaptureData(object):
    def __init__(self, id, date, image_path):
        self.id = id
        self.date = date
        self.pixmap = load_img(image_path)


def get_capture():
    data_list = []
    for i in range(10):
        now = datetime.datetime.now()
        date = '{}\n{}'.format(now.strftime('%Y-%m-%d'),
                               now.strftime('%H:%M:%S'))
        data = CaptureData(
            id='person-{}'.format(i),
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
