# Common
import sys
import time
import os
import hashlib
# QT
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5 import QtCore
from main_window import Ui_MainWindow


# #Misc
# import numpy as np
# import cv2


class MainWindow(QMainWindow):
    sig_all_img = pyqtSignal(list)

    def __init__(self):

        super().__init__()

        self.uic = Ui_MainWindow()

        self.uic.setupUi(self)

        self.imgs_path = []

        self.uic.btn_open_dataset.clicked.connect(self.slot_open_dataset)

        self.sig_all_img.connect(self.uic.current_frame.slot_get_imgs)

        self.uic.btn_sort.clicked.connect(self.slot_sort)

        self.uic.btn_overlap.clicked.connect(self.slot_overlap)

        self.uic.btn_begin.clicked.connect(self.slot_begin)

        self.new_imgs_path = []

        self.index = 0

    def slot_open_dataset(self):

        data_path = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

        if data_path is not None:

            for file in os.listdir(data_path):

                if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".JPG") or file.endswith(
                        ".PNG") or file.endswith(".jpeg") or file.endswith(".JPEG"):
                    self.imgs_path.append(os.path.join(data_path, file))

    def slot_overlap(self):

        len_ = len(self.imgs_path)
        for i in range(len_):
            if i < len_ - 1:
                if self.imgs_path[i].split('.')[0] == self.imgs_path[i + 1].split('.')[0]:
                    print('duplicate')
                    self.new_imgs_path.append(self.imgs_path[i])
        for file in self.new_imgs_path:
            self.imgs_path.remove(file)

        print(len(self.imgs_path))

    def slot_sort(self):
        self.imgs_path = sorted(self.imgs_path)
        print(self.imgs_path)

    def slot_begin(self):
        if self.imgs_path is not None:
            self.sig_all_img.emit(self.imgs_path)

    def slot_show_image(self):
        img = cv2.imread(self.imgs_path[2])
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        qt_img = QtGui.QImage(rgb_img.data, rgb_img.shape[1], rgb_img.shape[0], QtGui.QImage.Format_RGB888)
        self.uic.current_frame.setPixmap(
            QtGui.QPixmap.fromImage(qt_img).scaled(self.uic.current_frame.width(), self.uic.current_frame.height(),
                                                   Qt.KeepAspectRatio))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_win = MainWindow()

    main_win.show()

    sys.exit(app.exec())
