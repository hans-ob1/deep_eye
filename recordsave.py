from PyQt5.QtCore import QDate, QTime, QDateTime, Qt
import cv2
import os

class Recorder:

	vidWriter = None

	def __init__(self, frame_width, frame_height, fps):

		# standardize parameters
		self.fixed_Height = frame_height
		self.fixed_Width = frame_width
		self.fixed_fps = fps
		self.predefinedFilePath = ""

		self.datetime4display = QDateTime.currentDateTime().toString()
		self.time4processing = QTime.currentTime().toString(Qt.DefaultLocaleLongDate).split()
		self.date4processing = QDate.currentDate().toString(Qt.ISODate)

		# initialize video writer
		self.vidWriter = cv2.VideoWriter("demo.avi",cv2.VideoWriter_fourcc('M','J','P','G'), fps, (frame_width,frame_height))

	# Date/Time setter and getters
	def setDisplayLabel(self):
		self.datetime4display = QDateTime.currentDateTime().toString()

	def getDisplayLabel(self):
		self.setDisplayLabel()
		return self.datetime4display

	def setCurrentTime(self):
		timeRaw = QTime.currentTime().toString(Qt.DefaultLocaleLongDate).split()
		timeDiscrete = timeRaw[0].split(':')
		self.time4processing = timeDiscrete[0] + '_' + timeDiscrete[1] + '_' + timeDiscrete[2] + "_" + timeRaw[1]		

	def getCurrentTime(self): 
		self.setCurrentTime()
		return self.time4processing

	def setTodayDate(self):
		self.date4processing = QDate.currentDate().toString(Qt.ISODate)

	def getTodayDate(self):
		self.setTodayDate()
		return self.date4processing

	# Methods:
	def setPreDefinedFilePath(self, f_Path):
		self.predefinedFilePath = f_Path

	def invokeRecording(self):

		'''
			filepath format: /path/to/directory/
		'''
		completeFolderDir = predefinedFilePath + self.date4processing + '/'

		os.makedirs(os.path.dirname(completeFolderDir), exist_ok=True)
		completeFilePath = completeFolderDir + self.time4processing + '.avi'

		retval = self.vidWriter.open(completeFilePath, cv2.VideoWriter_fourcc('M','J','P','G'), self.fixed_fps, (self.fixed_Width,self.fixed_Height))

		return retval


	def killRecorder(self):
		self.videWriter.release()










