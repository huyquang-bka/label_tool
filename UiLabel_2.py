import os

from PyQt5 import QtGui
from PyQt5.QtWidgets import QLabel, QShortcut
from PyQt5.QtGui import QKeySequence, QPixmap, QPainter, QPen

from PyQt5.QtCore import Qt, QRect
import time

# Misc
import numpy as np
import cv2


class UiLabel(QLabel):
    imgs_path = []

    txt_path = []

    def __init__(self, parent):
        super().__init__()
        self.setMouseTracking(True)
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        self.current_class_index = 0

        self.mouse_pos = np.array([])

        self.id = []

        self.bbox_ = []

        self.flag_left = False
        self.flag_right = False

        self.qt_img = None
        self.img = None

        self.top_left = []
        self.bottom_right = []

        self.first_point = []
        self.second_point = []

        self.remove_top_left = []
        self.remove_bottom_right = []

        self.current_img_index = 0
        self.current_class_index = 0

        QShortcut(QKeySequence(Qt.Key_Left), self, activated=self.move_left)
        QShortcut(QKeySequence(Qt.Key_Right), self, activated=self.move_right)
        QShortcut(QKeySequence(Qt.Key_0), self, activated=self.Key_0)
        QShortcut(QKeySequence(Qt.Key_1), self, activated=self.Key_1)
        QShortcut(QKeySequence(Qt.Key_2), self, activated=self.Key_2)
        QShortcut(QKeySequence(Qt.Key_3), self, activated=self.Key_3)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print("Left button press")
            self.flag_left = True
            self.x0 = event.pos().x()
            self.y0 = event.pos().y()
            self.x1 = -1000
            self.first_point = [self.x0, self.y0]
            self.update()

        if event.button() == Qt.RightButton:
            print("Right button press")
            self.flag_right = True
            self.remove_top_left = [event.x(), event.y()]

    def mouseMoveEvent(self, event):
        self.mouse_pos = np.array([event.x(), event.y()])
        if self.flag_left:
            self.x1 = event.pos().x()
            self.y1 = event.pos().y()
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if (event.pos() in self.rect()) and self.flag_left:
                self.second_point = [event.pos().x(), event.pos().y()]
                x_top, y_top, x_bottom, y_bottom = self.two_point_to_xyxy(self.first_point, self.second_point)
                self.flag_left = False
                self.finish_draw()
                if x_bottom - x_top < 20:
                    return
                self.top_left.append([x_top, y_top])
                self.bottom_right.append([x_bottom, y_bottom])
                print("Top left: {}".format(self.top_left))
                print("Bottom right: {}".format(self.bottom_right))

            self.x0 = 0
            self.y0 = 0
            self.x1 = 0
            self.y1 = 0
            self.update()
            self.repaint()

        if (event.button() == Qt.RightButton) and (event.pos() in self.rect()):
            x0, y0 = self.remove_top_left
            x1, y1 = event.pos().x(), event.pos().y()
            for i in range(len(self.bottom_right)):
                if (x0 >= self.top_left[i][0]) and (y0 >= self.top_left[i][1]) and (x1 <= self.bottom_right[i][0]) and (
                        y1 <= self.bottom_right[i][1]):
                    self.top_left.remove(self.top_left[i])
                    self.bottom_right.remove(self.bottom_right[i])
                    # self.id.remove(self.id[i])
                    break

            self.x0 = 0
            self.y0 = 0
            self.x1 = 0
            self.y1 = 0
            self.update()
            self.repaint()

    def two_point_to_xyxy(self, first_point, second_point):
        x0, y0 = first_point
        x1, y1 = second_point
        x_top = min(x0, x1)
        y_top = min(y0, y1)
        x_bottom = max(x0, x1)
        y_bottom = max(y0, y1)
        return x_top, y_top, x_bottom, y_bottom

    def finish_draw(self):
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        self.update()
        self.repaint()

    def move_left(self):

        if self.current_img_index <= 0:
            self.current_img_index = 0
        else:
            self.current_img_index -= 1
        self.slot_get_imgs(self.imgs_path)
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        self.update()
        self.repaint()

    def move_right(self):
        if self.current_img_index >= len(self.imgs_path) - 1:
            self.current_img_index = len(self.imgs_path) - 1
        else:
            self.current_img_index += 1

        self.slot_get_imgs(self.imgs_path)
        self.save_txt()
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        self.update()
        self.repaint()

    def Key_0(self):
        self.current_class_index = 0
        self.id.append(self.current_class_index)
        print("KEY_0")

    def Key_1(self):
        self.current_class_index = 1
        self.id.append(self.current_class_index)

    def Key_2(self):
        self.current_class_index = 2
        self.id.append(self.current_class_index)

    def Key_3(self):
        self.current_class_index = 3
        self.id.append(self.current_class_index)

    def Key_4(self):
        self.current_class_index = 4
        self.id.append(self.current_class_index)

    def save_txt(self):
        w, h = self.img.shape[1], self.img.shape[0]
        size = np.asarray([w, h])
        path = self.imgs_path[self.current_img_index - 1].split('.')[0]

        print(self.id)
        if self.bottom_right:
            with open(path + ".txt", "w+") as f:
                for i in range(len(self.bottom_right)):
                    bbox = np.asarray([self.top_left[i][0], self.top_left[i][1], self.bottom_right[i][0],
                                       self.bottom_right[i][1]])
                    x_, y_, w_, h_ = self.convert_to_yolov5(bbox)

                    f.write("{} {} {} {} {}\n".format(self.id[i], x_, y_, w_, h_))

        self.top_left = []
        self.bottom_right = []

    def convert_to_yolov5(self, box):

        box_center_x = (box[0] + box[2]) / 2

        box_center_y = (box[1] + box[3]) / 2

        box_w_d = box[2] - box[0]

        box_h_d = box[3] - box[1]

        _x = box_center_x / self.width()

        _y = box_center_y / self.height()

        _w = box_w_d / self.width()

        _h = box_h_d / self.height()

        return (_x, _y, _w, _h)

    def convert_to_bbox(self, img, file):
        box = self.load_txt(file)
        bb = []
        (centerX, centerY, width, height) = box[1:5]
        w = self.width()
        h = self.height()
        Xcenter = centerX * w
        Xrect = Xcenter - width * w / 2
        Ycenter = centerY * h
        Yrect = Ycenter - height * h / 2
        Wrect = width * w
        Hrect = height * h
        box = np.array([Xrect, Yrect, Wrect, Hrect])
        bb.append(box)
        print(bb)
        return bb

    def slot_get_txts(self, list_txt):
        self.txt_path = list_txt

    def slot_get_imgs(self, list_):

        self.imgs_path = list_
        self.img = cv2.imread(list_[self.current_img_index])
        rgb_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)

        self.qt_img = QPixmap.fromImage(
            QtGui.QImage(rgb_img.data, rgb_img.shape[1], rgb_img.shape[0], QtGui.QImage.Format_RGB888)).scaled(
            self.width(), self.height(), Qt.KeepAspectRatioByExpanding)

    def check_label(self):
        for i in range(len(self.txt_path)):

            if self.imgs_path[self.current_img_index].split('.')[0] == self.txt_path[i].split('.')[0]:
                img = cv2.imread(self.imgs_path[self.current_img_index])
                self.bbox_ = self.convert_to_bbox(img, self.txt_path[i])

    def load_txt(self, file):
        arr_ = np.loadtxt(file)
        arr_ = np.asarray(arr_)

        return arr_

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.qt_img is not None:
            painter.drawPixmap(self.rect(), self.qt_img)

        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
        rect = QRect(self.x0, self.y0, abs(self.x1 - self.x0), abs(self.y1 - self.y0))
        painter.drawRect(rect)
        for i in range(len(self.bottom_right)):
            painter.drawRect(
                QRect(self.top_left[i][0], self.top_left[i][1], self.bottom_right[i][0] - self.top_left[i][0],
                      self.bottom_right[i][1] - self.top_left[i][1]))

        for i in range(len(self.txt_path)):
            if self.imgs_path[self.current_img_index].split('.')[0] == self.txt_path[i].split('.')[0]:
                print(self.imgs_path[self.current_img_index])
                print(self.txt_path[i])
                img = cv2.imread(self.imgs_path[self.current_img_index])
                self.bbox_ = self.convert_to_bbox(img, self.txt_path[i])
                for j in range(len(self.bbox_)):
                    print(self.bbox_[0][0], self.bbox_[0][1], self.bbox_[0][2], self.bbox_[0][3])
                    painter.drawRect(QRect(self.bbox_[0][0], self.bbox_[0][1], self.bbox_[0][2], self.bbox_[0][3]))

        if self.mouse_pos.size == 2:
            painter.setPen(QPen(Qt.green, 3, Qt.SolidLine))
            painter.drawText(self.mouse_pos[0], self.mouse_pos[1], str(self.current_class_index))
        self.update()
        super().paintEvent(event)
