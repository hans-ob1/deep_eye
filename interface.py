from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sys
import cv2
import numpy as np
import threading
import time
import queue

from recordsave import Recorder
from ssd_engine import SSD_Detector
from motiondetector import MotionDetector

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
        self.timetracker = -1

        self.subjectCheck.stateChanged.connect(self.record_on_detection)
        self.recordOnPresence = False
        self.inactiveCount = 0
        self.list_of_obj = 0

        self.motionCheck.stateChanged.connect(self.record_on_motion)
        self.recordOnMotion = False
        self.isMoving = False
        self.noMotionCount = 0

        self.motionTagLocation = (CAM_WIDTH-300,30)
        self.motionTagColour = (0,0,255)

        # Detector object
        self.detector = SSD_Detector()

        # Motion detector object
        self.motiondetect = MotionDetector()

    def record_to(self):

        if self.record.getPreDefinedFilePath() == "undefined":
            # return filepath where video is saved
            dir_ = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select a folder for record output:', '~/', QtWidgets.QFileDialog.ShowDirsOnly)

            if len(dir_) > 0:
                self.record.setPreDefinedFilePath(dir_)
                self.filepathText.setText('Saving video to: ' + dir_)
            else:
                self.record.setPreDefinedFilePath("undefined")

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
            self.recordOnPresence = True
        else:
            self.recordOnPresence = False

    def record_on_motion(self):
        if self.motionCheck.isChecked():
            self.recordOnMotion = True
        else:
            self.recordOnMotion = False

    def recordTriggerFunc(self, frame):
        # record on presence only
        if self.recordOnPresence and not self.recordOnMotion:
            if len(self.list_of_obj) > 0:

                if self.inactiveCount >= 60: # estimate 2 sec of detect nothing
                    self.record.invokeRecording() #reinitalize

                self.record.vidWriter.write(frame)
                self.inactiveCount = 0
            else:

                if self.inactiveCount < 60:
                    self.inactiveCount += 1
                else:
                    self.record.killRecorder()

        elif self.recordOnMotion and not self.recordOnPresence:
            if self.isMoving:
                if self.noMotionCount >= 60:
                    self.record.invokeRecording()

                self.record.vidWriter.write(frame)
                self.noMotionCount = 0
            else:
                if self.noMotionCount < 60:
                    self.noMotionCount += 1
                else:
                    self.record.killRecorder()

        elif self.recordOnMotion and self.recordOnPresence:
            if len(self.list_of_obj) > 0 or self.isMoving:
                if self.inactiveCount >= 60 and self.noMotionCount >= 60:
                    self.record.invokeRecording()
                self.record.vidWriter.write(frame)
                self.inactiveCount = 0
                self.noMotionCount = 0
            else:
                assessOne = False
                assessTwo = False

                if self.noMotionCount < 60:
                    self.noMotionCount += 1
                else:
                    assessOne = True
                if self.inactiveCount < 60:
                    self.inactiveCount += 1
                else:
                    assessTwo = True

                if assessOne and assessTwo:
                    self.record.killRecorder()
        else:
            # Record everything in interval of 5 minutes
            if self.timetracker == -1:
                self.timetracker = self.record.getCurrentTime()
            else:
                ref_hr, ref_min, ref_sec, _ = self.timetracker.split('_')
                refTimeInSeconds = int(ref_min)*60 + int(ref_sec)

                cur_hr, cur_min, cur_sec, _ = self.record.getCurrentTime().split('_')
                curTimeInSeconds = int(cur_min)*60 + int(cur_sec)

                if curTimeInSeconds - refTimeInSeconds >= 5:
                    self.record.invokeRecording()
                    self.timetracker = self.record.getCurrentTime()
            
            self.record.vidWriter.write(frame)



    def drawOnFrame(self, inputImg, isMotion):
        # Tag date
        cv2.putText(inputImg,self.record.getDisplayLabel(),
                        self.datetimeTagLocation, 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        1,
                        self.datetimeTagColour,
                        2,
                        cv2.LINE_AA)

        # Tag motion indicator        
        if isMotion:
            cv2.putText(inputImg,"Motion Detected!",
                            self.motionTagLocation, 
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            1,
                            self.motionTagColour,
                            2,
                            cv2.LINE_AA)            

    def displayFrame(self, img):
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

    # Live Mode
    def update_frame(self):
        if not q.empty():

            # UI thingy
            self.recordButton.setEnabled(True)
            self.displayText.setText('')

            # grab frame from video thread
            frame = q.get()
            img = frame["img"]

            if self.recordOnMotion:
                # detect motion
                motionImg = img.copy()
                self.isMoving = self.motiondetect.detectmotion(motionImg)

            if self.recordOnPresence:
                # detect objects and indicate on display
                img, self.list_of_obj = self.detector.process_image(img)


            # Tag the frame with indications
            self.drawOnFrame(img,self.isMoving)

            if self.record.getRecordingStatus():
                self.recordTriggerFunc(img)

            # show frame with annotation
            self.displayFrame(img)

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
