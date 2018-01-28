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
from settings import EmailSender

# Cam Params
CAM_WIDTH = 1280
CAM_HEIGHT = 720
CAM_FPS = 30

# (record everything mode) This parameter determines the intervals of recording
RECORD_INTERVAL = 300 # in seconds

# (smart recording mode) This parameter determines how many more frames to save after inactivity
RECORD_EXTENSION = 60 # in frame counts

# Threading variables
cam_running = False
capture_thread = None
q = queue.Queue()

# load UI
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

    print("Terminated camera feed")
    

class MyWindowClass(QtWidgets.QMainWindow, form_class):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        # obtain dim of elements
        self.triggerGroupDim = [self.triggerGroup.geometry().width(),self.triggerGroup.geometry().height()]
        self.recordButtonDim = [self.recordButton.geometry().width(),self.recordButton.geometry().height()]
        self.filepathTextDim = [self.filepathText.geometry().width(),self.filepathText.geometry().height()]

        # Livefeed tab:
        self.window_width = self.live_display.frameSize().width()
        self.window_height = self.live_display.frameSize().height()
        self.live_display.setStyleSheet("QLabel { background-color : black}")  

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
        self.isDetected = False

        self.motionCheck.stateChanged.connect(self.record_on_motion)
        self.recordOnMotion = False
        self.isMoving = False
        self.noMotionCount = 0

        self.motionTagLocation = (CAM_WIDTH-300,30)
        self.motionTagColour = (0,0,255)

        # Detector object
        self.detector = SSD_Detector()
        if not self.detector.ready:
            self.subjectCheck.setEnabled(False)

        # Motion detector object
        self.motiondetect = MotionDetector()

        # email alert module
        self.emailsender = EmailSender()

    def resizeEvent(self,event):
        # readjust ui according to window size
        # MainWindow.textEdit.setGeometry(QtCore.QRect(30, 80, 341, 441))

        curr_mainframe_w = self.frameSize().width()
        curr_mainframe_h = self.frameSize().height()

        # Adjust tab widget size
        fixed_tab_x = self.tabWidget.geometry().x()
        fixed_tab_y = self.tabWidget.geometry().y()
        new_tab_w = curr_mainframe_w - 40
        new_tab_h = curr_mainframe_h - 80

        self.tabWidget.resize(new_tab_w,new_tab_h)

        # **** Set all elements relative to tabWidget_relativeSizeRatio ****

        # set triggerGroup Pos:
        new_trigger_x = fixed_tab_x + (new_tab_w - self.triggerGroupDim[0] - 40)
        new_trigger_y = fixed_tab_y
        self.triggerGroup.move(new_trigger_x,new_trigger_y)

        # set recordButton Pos:
        new_recordbtn_x = fixed_tab_x + (new_tab_w/2 - self.recordButtonDim[0])
        new_recordbtn_y = fixed_tab_y + (new_tab_h - self.recordButtonDim[1] - 80)
        self.recordButton.move(new_recordbtn_x,new_recordbtn_y)

        # set filePath Pos:
        new_filepath_x = fixed_tab_x
        new_filepath_y = new_recordbtn_y - self.filepathTextDim[1] - 20
        self.filepathText.move(new_filepath_x,new_filepath_y)

        # finally set the display size
        self.window_width = new_trigger_x - 40
        self.window_height = new_filepath_y - 40
        self.live_display.resize(self.window_width,self.window_height)

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
            if self.isDetected:

                if self.inactiveCount >= RECORD_INTERVAL: # estimate 2 sec of detect nothing
                    self.record.invokeRecording() #reinitalize

                self.record.vidWriter.write(frame)
                self.inactiveCount = 0
            else:

                if self.inactiveCount < RECORD_INTERVAL:
                    self.inactiveCount += 1
                else:
                    self.record.killRecorder()

        elif self.recordOnMotion and not self.recordOnPresence:
            if self.isMoving:
                if self.noMotionCount >= RECORD_INTERVAL:
                    self.record.invokeRecording()

                self.record.vidWriter.write(frame)
                self.noMotionCount = 0
            else:
                if self.noMotionCount < RECORD_INTERVAL:
                    self.noMotionCount += 1
                else:
                    self.record.killRecorder()

        elif self.recordOnMotion and self.recordOnPresence:
            if self.isDetected or self.isMoving:
                if self.inactiveCount >= RECORD_INTERVAL and self.noMotionCount >= RECORD_INTERVAL:
                    self.record.invokeRecording()
                self.record.vidWriter.write(frame)
                self.inactiveCount = 0
                self.noMotionCount = 0
            else:
                assessOne = False
                assessTwo = False

                if self.noMotionCount < RECORD_INTERVAL:
                    self.noMotionCount += 1
                else:
                    assessOne = True
                if self.inactiveCount < RECORD_INTERVAL:
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

                if curTimeInSeconds - refTimeInSeconds >= RECORD_INTERVAL:
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
        pix = QtGui.QPixmap(image)
        self.live_display.setPixmap(pix)

    # Live Mode
    def update_frame(self):
        if not q.empty():

            # UI thingy
            self.recordButton.setEnabled(True)

            # grab frame from video thread
            frame = q.get()
            img = frame["img"]

            if self.recordOnMotion:
                # detect motion
                motionImg = img.copy()
                self.isMoving = self.motiondetect.detectmotion(motionImg)
            else:
                self.isMoving = False

            if self.recordOnPresence:
                # detect objects and indicate on display
                img, self.isDetected = self.detector.process_image(img)


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
    w.setWindowTitle('Deepeye 2018')
    w.show()
    app.exec_()

main()
