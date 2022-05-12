# QT
from PyQt5 import QtGui
from PyQt5.QtWidgets import QLabel, QShortcut
from PyQt5.QtGui import QKeySequence, QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QRect
from check_point_rect import two_point_to_xyxy
from string import digits

# Misc
import cv2


# import cv2

class UiLabel(QLabel):
    imgs_path = []

    def __init__(self, parent=None):
        super().__init__()
        self.setMouseTracking(True)
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        self.flag_left = False
        self.flag_right = False

        self.qt_img = None

        self.first_point = []
        self.second_point = []

        self.top_left = []
        self.bottom_right = []

        self.remove_first_point = []
        self.remove_second_point = []

        self.current_img_index = 0
        self.id = ""

        self.current_class_index = 0

        QShortcut(QKeySequence(Qt.Key_Left), self, activated=self.move_left)
        QShortcut(QKeySequence(Qt.Key_Right), self, activated=self.move_right)
        QShortcut(QKeySequence(Qt.Key_0), self, activated=lambda: print(Qt.Key_0))
        QShortcut(QKeySequence(Qt.Key_1), self, activated=lambda: print(Qt.Key_1))
        QShortcut(QKeySequence(Qt.Key_2), self, activated=lambda: print(Qt.Key_2))
        QShortcut(QKeySequence(Qt.Key_3), self, activated=lambda: print(Qt.Key_3))

    def finish_draw(self):
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        self.update()
        self.repaint()

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
            self.remove_first_point = [event.x(), event.y()]

    def mouseMoveEvent(self, event):
        if self.flag_left:
            self.x1 = event.pos().x()
            self.y1 = event.pos().y()
            # if self.x1 == self.x0:
            #     self.x1 = self.x0 + 1
            # if self.y1 == self.y0:
            #     self.y1 = self.y0 + 1
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if (event.pos() in self.rect()) and self.flag_left:
                self.second_point = [event.pos().x(), event.pos().y()]
                x_top, y_top, x_bottom, y_bottom = two_point_to_xyxy(self.first_point, self.second_point)
                self.flag_left = False
                self.finish_draw()
                if x_bottom - x_top < 10:
                    return
                self.top_left.append([x_top, y_top])
                self.bottom_right.append([x_bottom, y_bottom])
                print("Top left: {}".format(self.top_left))
                print("Bottom right: {}".format(self.bottom_right))
                # self.repaint()

        if (event.button() == Qt.RightButton) and (event.pos() in self.rect()):
            x0, y0 = self.remove_first_point
            x1, y1 = event.pos().x(), event.pos().y()
            for i in range(len(self.bottom_right)):
                if (x0 >= self.top_left[i][0]) and (y0 >= self.top_left[i][1]) and (x1 <= self.bottom_right[i][0]) and (
                        y1 <= self.bottom_right[i][1]):
                    self.top_left.remove(self.top_left[i])
                    self.bottom_right.remove(self.bottom_right[i])
                    break
            print("Top left: {}".format(self.top_left))
            print("Bottom right: {}".format(self.bottom_right))

    def next_img(self):
        with open("spot.txt", "w+") as f:
            for i in range(len(self.bottom_right)):
                x, y, w, h = self.top_left[i][0], self.top_left[i][1], self.bottom_right[i][0] - self.top_left[i][0], \
                             self.bottom_right[i][1] - self.top_left[i][1]
                print("x, y, w, h: {}".format([x, y, w, h]))
                f.write("{} {} {} {}\n".format(x, y, w, h))
        self.current_img_index += 1
        self.top_left = []
        self.bottom_right = []
        self.finish_draw()

    def slot_get_imgs(self, list_):

        # self.current_img_index = self.move_right()
        # print(self.current_img_index)
        # img = cv2.imread(list_[self.current_img_index])
        img = cv2.imread(list_[0])
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.qt_img = QPixmap.fromImage(
            QtGui.QImage(rgb_img.data, rgb_img.shape[1], rgb_img.shape[0], QtGui.QImage.Format_RGB888)).scaled(
            self.width(), self.height())
        # self.setPixmap(self.rect(), self.qt_img)

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.qt_img is not None:
            painter.drawPixmap(self.rect(), self.qt_img)
        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
        if self.x1 != -1000:
            x1, y1, x2, y2 = two_point_to_xyxy([self.x0, self.y0], [self.x1, self.y1])
            rect = QRect(x1, y1, x2 - x1, y2 - y1)
            painter.drawRect(rect)

        for i in range(len(self.bottom_right)):
            x, y, w, h = self.top_left[i][0], self.top_left[i][1], self.bottom_right[i][0] - self.top_left[i][0], \
                         self.bottom_right[i][1] - self.top_left[i][1]
            painter.drawRect(QRect(x, y, w, h))
            painter.drawText(x, y, str(self.id))

        self.update()

    def move_right(self):
        if self.current_img_index < len(self.list_) - 1:
            self.current_img_index += 1

    def move_left(self):
        if self.current_img_index > 0:
            self.current_img_index -= 1
