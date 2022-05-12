# QT
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QShortcut
from PyQt5.QtGui import QKeySequence, QPixmap, QPainter, QPen
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtCore
from PyQt5.QtCore import QPoint, Qt, QRect
import time

# Misc
import numpy as np
import cv2


# import cv2

class UiLabel(QLabel):
    imgs_path = []

    def __init__(self, parent):

        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        self.flag_left = False
        self.flag_right = False
        self.time_click = 0.1
        self.start_press = 0

        self.qt_img = None

        super().__init__()
        self.top_left = []
        self.bottom_right = []

        self.remove_top_left = []
        self.remove_bottom_right = []

        self.current_img_index = 0

        QShortcut(QKeySequence(Qt.Key_Left), self, activated=self.move_left)

        QShortcut(QKeySequence(Qt.Key_Right), self, activated=self.move_right)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_press = time.time()
            print("Left button press")
            self.flag_left = True
            self.x0 = event.x()
            self.y0 = event.y()
            self.top_left.append([self.x0, self.y0])
            self.update()

        if event.button() == Qt.RightButton:
            print("Right button press")
            self.flag_right = True
            self.remove_top_left = [event.x(), event.y()]

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

        if self.current_img_index >= len(self.imgs_path)-1:
            self.current_img_index = len(self.imgs_path) - 1
        else:
            self.current_img_index += 1

        self.slot_get_imgs(self.imgs_path)
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        self.update()
        self.repaint()

    def mouseMoveEvent(self, event):
        if self.flag_left == True:
            self.x1 = event.x()
            self.y1 = event.y()
            self.update()

    def mouseReleaseEvent(self, event):
        if (event.button() == Qt.LeftButton) and (event.pos() in self.rect()) and self.flag_left and (
                time.time() - self.start_press < self.time_click):
            self.bottom_right.append([event.pos().x(), event.pos().y()])
            print("Top left: {}".format(self.top_left))
            print("Bottom right: {}".format(self.bottom_right))
            self.flag_left = False
            # self.repaint()

        if (event.button() == Qt.RightButton) and (event.pos() in self.rect()):
            x0, y0 = self.remove_top_left
            x1, y1 = event.pos().x(), event.pos().y()
            for i in range(len(self.bottom_right)):
                if (x0 >= self.top_left[i][0]) and (y0 >= self.top_left[i][1]) and (x1 <= self.bottom_right[i][0]) and (
                        y1 <= self.bottom_right[i][1]):
                    self.top_left.remove(self.top_left[i])
                    self.bottom_right.remove(self.bottom_right[i])
                    break
            self.x0 = 0
            self.y0 = 0
            self.x1 = 0
            self.y1 = 0
            self.update()
            self.repaint()

    def slot_get_imgs(self, list_):

        self.imgs_path = list_
        img = cv2.imread(list_[self.current_img_index])
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        self.qt_img = QPixmap.fromImage(
            QtGui.QImage(rgb_img.data, rgb_img.shape[1], rgb_img.shape[0], QtGui.QImage.Format_RGB888)).scaled(
            self.width(),
            self.height())
        self.update()

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

        super().paintEvent(event)
        self.update()
