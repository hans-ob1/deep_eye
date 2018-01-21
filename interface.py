from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sys
import cv2
import numpy as np
import threading
import time
import queue

from recordsave import Recorder
from ssd_engine import SSD_Detector

# Cam Params
CAM_WIDTH = 1280
CAM_HEIGHT = 720
CAM_FPS = 30

cam_running = False
capture_thread = None
q = queue.Queue()

# interfacing UI
form_class = uic.loadUiType("interface.ui")[0]

 
# parallel threaded camera feed
def grab(cam, queue, width, height, fps):
    global cam_running
    cam_running = True

    capture = cv2.VideoCapture(cam)
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

    print("thread killed")


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
        
        # Livefeed tab:
        self.window_width = self.live_widget.frameSize().width()
        self.window_height = self.live_widget.frameSize().height()
        self.live_widget = OwnImageWidget(self.live_widget)       

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)

        self.datetimeTagLocation = (10,30)
        self.datetimeTagColour = (0,255,0)

        # Recorder object
        self.record = Recorder(CAM_WIDTH, CAM_HEIGHT, CAM_FPS)
        self.recordButton.clicked.connect(self.record_to)

        self.subjectCheck.stateChanged.connect(self.record_on_detection)
        self.recordSubjectActivity = False
        self.inactiveCount = 0

        # Detector object
        self.detector = SSD_Detector()

    def record_to(self):

        if self.record.getPreDefinedFilePath() == "undefined":
            # return filepath where video is saved
            dir_ = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select a folder for record output:', '~/', QtWidgets.QFileDialog.ShowDirsOnly)
            self.record.setPreDefinedFilePath(dir_)
            self.filepathText.setText('Saving video to: ' + dir_)

        else:
            if self.record.getRecordingStatus():
                # stop recording
                self.record.turnOffRecording()
                self.recordButton.setText('Record')
            else:
                self.record.invokeRecording()

                if self.record.getRecordingStatus():
                    self.recordButton.setText('Stop')

    def record_on_detection(self):
        if self.subjectCheck.isChecked():
            self.recordSubjectActivity = True
        else:
            self.recordSubjectActivity = False     


    # Live Mode
    def update_frame(self):
        if not q.empty():

            # UI thingy
            self.recordButton.setEnabled(True)
            self.displayText.setText('')

            frame = q.get()
            img = frame["img"]

            # tag datetime to each frame
            cv2.putText(img,self.record.getDisplayLabel(),self.datetimeTagLocation, cv2.FONT_HERSHEY_SIMPLEX, 1,self.datetimeTagColour,2,cv2.LINE_AA)

            if self.record.getRecordingStatus():
                if self.recordSubjectActivity: 
                    # detect objects
                    img, list_of_obj = self.detector.process_image(img)

                    if len(list_of_obj) > 0:

                        if self.inactiveCount > 60:
                            self.record.invokeRecording() #reinitalize
    
                        self.record.vidWriter.write(img)
                        self.inactiveCount = 0
                    else:
                        self.inactiveCount += 1


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
            self.live_widget.setImage(image)

    def closeEvent(self, event):
        global cam_running
        cam_running = False
        self.record.killRecorder()


def main():
    capture_thread = threading.Thread(target=grab, args = (0, q, CAM_WIDTH, CAM_HEIGHT, CAM_FPS))
    capture_thread.start()

    app = QtWidgets.QApplication(sys.argv)
    w = MyWindowClass(None)
    w.setWindowTitle('DeepEye 2018')
    w.show()
    app.exec_()

main()
