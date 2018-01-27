from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sys
import cv2
import numpy as np
import threading
import time
import queue

from playback import Player

# Cam Params
cam_running = False
capture_thread = None
q = queue.Queue()

# Playback Params
video_running = False
video_thread = None
vid = queue.Queue()

# interfacing UI
form_class = uic.loadUiType("label_display_beta.ui")[0]

def grab(cam, queue, width, height, fps):
    global cam_running
    cam_running = True

    capture = cv2.VideoCapture(0)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    capture.set(cv2.CAP_PROP_FPS, fps)

    while(cam_running):
        frame = {}        
        capture.grab()
        retval, img = capture.retrieve(0)
        frame["img"] = img

        if queue.qsize() < 10:
            queue.put(frame)
        else:
            print (queue.qsize())

class OwnImageWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(OwnImageWidget, self).__init__(parent)
        self.image = None

    def setImage(self, image):
        self.image = image
        sz = image.size()
        self.setMinimumSize(sz)
        self.update()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.image:
            qp.drawImage(QtCore.QPoint(0, 0), self.image)
        qp.end()



class MyWindowClass(QtWidgets.QMainWindow, form_class):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self) 

        MainFrame_Width = self.frameSize().width()
        MainFrame_Height = self.frameSize().height()
        self.tabWidget_relativeSizeRatio = [self.tabWidget.geometry().width()/MainFrame_Width,
                                            self.tabWidget.geometry().height()/MainFrame_Height]
        self.liveWidget_relativeSizeRatio = [self.live_display.geometry().width()/MainFrame_Width,
                                            self.live_display.geometry().height()/MainFrame_Height]

        self.window_width = self.live_display.frameSize().width()
        self.window_height = self.live_display.frameSize().height()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)


    def resizeEvent(self,event):
        # readjust ui according to window size
        # MainWindow.textEdit.setGeometry(QtCore.QRect(30, 80, 341, 441))

        curr_mainframe_w = self.frameSize().width()
        curr_mainframe_h = self.frameSize().height()

        # new TabWidget Size
        x = self.tabWidget.geometry().x()
        y = self.tabWidget.geometry().y()

        new_width = int(self.tabWidget_relativeSizeRatio[0] * curr_mainframe_w)
        new_height = int(self.tabWidget_relativeSizeRatio[1] * curr_mainframe_h)

        self.tabWidget.setGeometry(x,y,new_width,new_height)

        # new live display Size
        new_width = int(self.liveWidget_relativeSizeRatio[0] * curr_mainframe_w)
        new_height = int(self.liveWidget_relativeSizeRatio[1] * curr_mainframe_h)

        self.window_width = new_width
        self.window_height = new_height

        self.live_display.resize(new_width, new_height)


    # Live Mode
    def update_frame(self):
        if not q.empty():

            frame = q.get()
            img = frame["img"]

            img_height, img_width, img_colors = img.shape
            scale_w = float(self.window_width) / float(img_width)
            scale_h = float(self.window_height) / float(img_height)
            scale = min([scale_w, scale_h])

            if scale == 0:
                scale = 1
            
            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation = cv2.INTER_CUBIC)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            
            height, width, bpc = img.shape
            bpl = bpc * width
            image = QtGui.QImage(img.data, width, height, bpl, QtGui.QImage.Format_RGB888)
            pix = QtGui.QPixmap(image)
            self.live_display.setPixmap(pix)


    def closeEvent(self, event):
        global cam_running
        cam_running = False


def main():
    capture_thread = threading.Thread(target=grab, args = (0, q, 1280, 720, 60))
    capture_thread.start()

    app = QtWidgets.QApplication(sys.argv)
    w = MyWindowClass(None)
    w.setWindowTitle('DeepCam 2018')
    w.show()
    app.exec_()

main()
