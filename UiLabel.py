#Common
import sys
import time

#QT
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtCore
from PyQt5.QtCore import QPoint, Qt


#Misc
import numpy as np
import cv2

class UiLabel(QLabel):

    imgs_path = []
    
    current_img_index = 0
    
    def __init__(self,parent):
        
        print("UILABEL is initted!")
        
        super().__init__()
        
        QShortcut(QKeySequence(Qt.Key_Left), self, activated=self.move_left)
        
        QShortcut(QKeySequence(Qt.Key_Right), self, activated=self.move_right)
        
    def mousePressEvent(self, event):
        
        if event.button() == Qt.LeftButton:
            
            print("Left button press")

    def mouseReleaseEvent(self, event):

        if (event.button() == Qt.LeftButton) and (event.pos() in self.rect()):
                
                print("Left button release {}".format(event.pos()))
        
    
    def move_left(self):
        
        print("move_left")
        
    def move_right(self):
    
        print("move_right")
        
    def slot_get_imgs(self,list_):
    
        imgs_path = list_