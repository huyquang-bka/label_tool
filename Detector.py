#Common
import argparse
import os
import sys
from pathlib import Path
import numpy as np

#Torch
import torch
import torch.backends.cudnn as cudnn

#QT
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow

from PyQt5.QtCore import pyqtSignal

#Misc
from models.common import DetectMultiBackend
from utils.datasets import IMG_FORMATS, VID_FORMATS, LoadImages, LoadStreams
from utils.general import (LOGGER, check_file, check_img_size, check_imshow, check_requirements, colorstr, cv2,
                           increment_path, non_max_suppression, print_args, scale_coords, strip_optimizer, xyxy2xywh)
from utils.plots import Annotator, colors, save_one_box
from utils.torch_utils import select_device, time_sync

#MAIN
class DetectorThread(QtCore.QThread):
    
    signal = pyqtSignal(np.ndarray)
    
    def __init__(self, index=0):
        super().__init__()
        #id
        self.index = index
        #VARIABLES
        self.source='C:/Videos/quy0.avi'        # file/dir/URL/glob, 0 for webcam
        self.model_file='yolov5s.pt'
        self.data='data/coco128.yaml'        # dataset.yaml path
        self.imgsz=(640, 640)                # inference size (height, width)
        self.conf_thres=0.25                 # confidence threshold
        self.iou_thres=0.45                  # NMS IOU threshold
        self.max_det=1000                    # maximum detections per image
        self.device=0                        # cuda device, i.e. 0 or 0,1,2,3 or cpu
        self.save_crop=False                 # save cropped prediction boxes
        self.classes=None                    # filter by class: --class 0, or --class 0 2 3
        self.agnostic_nms=False              # class-agnostic NMS
        self.line_thickness=1                # bounding box thickness (pixels)
        self.hide_labels=False               # hide labels
        self.hide_conf=False                 # hide confidences
        self.half=False                      # use FP16 half-precision inference
        self.dnn=False                       # use OpenCV DNN for ONNX inference

    def setup(self, a_source, a_model):
        self.source = a_source
        self.model_file = a_model
    
    @torch.no_grad()
    def run(self):
        print('Starting thread...', self.index)
        self.source     = str(self.source)
        is_file = Path(self.source).suffix[1:] in (IMG_FORMATS + VID_FORMATS)
        is_url  = self.source.lower().startswith(('rtsp://', 'rtmp://', 'http://', 'https://'))
       
        if is_url and is_file:
            self.source = check_file(self.source)  # download

        # Load model
        self.device = select_device(self.device)
        model = DetectMultiBackend(self.model_file, device=self.device, dnn=self.dnn, data=self.data, fp16=self.half)
        stride, names, pt = model.stride, model.names, model.pt
        self.imgsz = check_img_size(self.imgsz, s=stride)  # check image size

        # Dataloader
        dataset = LoadImages(self.source, img_size=self.imgsz, stride=stride, auto=pt)
        bs = 1  # batch_size
        
        vid_path, vid_writer = [None] * bs, [None] * bs

        # Run inference
        model.warmup(imgsz=(1 if pt else bs, 3, *self.imgsz))  # warmup
        dt, seen = [0.0, 0.0, 0.0], 0
        for path, im, im0s, vid_cap, s in dataset:
            t1 = time_sync()
            im = torch.from_numpy(im).to(self.device)
            im = im.half() if model.fp16 else im.float()  # uint8 to fp16/32
            im /= 255  # 0 - 255 to 0.0 - 1.0
            if len(im.shape) == 3:
                im = im[None]  # expand for batch dim
            t2 = time_sync()
            dt[0] += t2 - t1

            # Inference 
            pred = model(im, augment=False, visualize=False)
            t3 = time_sync()
            dt[1] += t3 - t2

            # NMS
            pred = non_max_suppression(pred, self.conf_thres, self.iou_thres, self.classes, self.agnostic_nms, max_det=self.max_det)
            dt[2] += time_sync() - t3

            # Second-stage classifier (optional)
            # pred = utils.general.apply_classifier(pred, classifier_model, im, im0s)

            # Process predictions
            for i, det in enumerate(pred):  # per image
                seen += 1

                p, im0, frame = path, im0s.copy(), getattr(dataset, 'frame', 0)

                p = Path(p)  # to Path
                s += '%gx%g ' % im.shape[2:]  # print string
                gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
                imc = im0.copy() if self.save_crop else im0  # for save_crop
                annotator = Annotator(im0, line_width=self.line_thickness, example=str(names))
                if len(det):
                    # Rescale boxes from img_size to im0 size
                    det[:, :4] = scale_coords(im.shape[2:], det[:, :4], im0.shape).round()

                    # Print results
                    for c in det[:, -1].unique():
                        n = (det[:, -1] == c).sum()  # detections per class
                        s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                    # Write results
                    for *xyxy, conf, cls in reversed(det):
                        c = int(cls)  # integer class
                        label = None if self.hide_labels else (names[c] if self.hide_conf else f'{names[c]} {conf:.2f}')
                        annotator.box_label(xyxy, label, color=colors(c, True))
                        if self.save_crop:
                            save_one_box(xyxy, imc, file=save_dir / 'crops' / names[c] / f'{p.stem}.jpg', BGR=True)

                # Stream results
                im0 = annotator.result()
                #cv2.imshow('Result', im0) #for displaying
                self.signal.emit(im0)
                cv2.waitKey(1)
    def stop(self):
        print('Stopping thread...', self.index)
        self.terminate()