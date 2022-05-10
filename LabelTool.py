#Common
import sys
import time
import os

#QT
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtCore 
from main_window import Ui_MainWindow


#Misc
import numpy as np
import cv2


class MainWindow(QMainWindow):

    sig_all_img = pyqtSignal(list)
    
    def __init__(self):
        
        super().__init__()
        
        self.uic = Ui_MainWindow()
        
        self.uic.setupUi(self)

        self.imgs_path = []

        self.uic.btn_open_dataset.clicked.connect(self.slot_open_dataset)
        
        self.sig_all_img.connect(self.uic.current_frame.slot_get_imgs)
        
    def slot_open_dataset(self):
        
        data_path = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        
        for file in os.listdir(data_path):
        
            if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".JPG") or file.endswith(".PNG"):
        
                self.imgs_path.append(os.path.join(data_path, file))
                
        self.sig_all_img.emit(self.imgs_path)


if __name__ == "__main__":

    app = QApplication(sys.argv)

    main_win = MainWindow()

    main_win.show()

    sys.exit(app.exec())