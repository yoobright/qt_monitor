# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
from PyQt5.QtGui import QPixmap
def updateVideo():
    pass


class CaptureData(object):
    def __init__(self, id, date, image_path):
        self.id = id
        self.date = date
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            pixmap = QPixmap('images/person.png')
        self.pixmap = pixmap


def get_capture():
    data_list = []
    for i in range(10):
        now = datetime.datetime.now()
        date = '{}\n{}'.format(now.strftime('%Y/%m/%d'),
                               now.strftime('%H:%M:%S'))
        data = CaptureData(
            id='person-{}'.format(i),
            date=date,
            image_path='person.png'
        )
        data_list.append(data)
    return data_list