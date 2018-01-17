from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sys
import cv2
import numpy as np
import threading
import time
import queue

from recordsave import Recorder

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

        # Recorder object
        self.record = Recorder(CAM_WIDTH, CAM_HEIGHT, CAM_FPS)
        self.recordButton.clicked.connect(self.record_to)

    def record_to(self):

        if self.record.getPreDefinedFilePath() == "undefined":
            # return filepath where video is saved
            dir_ = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select a folder:', '~/', QtWidgets.QFileDialog.ShowDirsOnly)
            self.record.setPreDefinedFilePath(dir_)
            self.filepathText.setText('Saving to: ' + dir_)

        else:

            if self.record.getRecordingStatus():
                # stop recording
                self.record.turnOffRecording()
                self.recordButton.setText('Record')
            else:
                self.record.invokeRecording()

                if self.record.getRecordingStatus():
                    self.recordButton.setText('Stop')



    # Live Mode
    def update_frame(self):
        if not q.empty():

            # UI thingy
            self.recordButton.setEnabled(True)
            self.displayText.setText('')

            frame = q.get()
            img = frame["img"]

            # tag datetime to each frame
            cv2.putText(img,self.record.getDisplayLabel(),(10,30), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),2,cv2.LINE_AA)

            # record file
            if self.record.getRecordingStatus():
                self.record.vidWriter.write(img)

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
    w.setWindowTitle('DeepCam 2018')
    w.show()
    app.exec_()

main()
