from PyQt5.QtCore import QDate, QTime, QDateTime, Qt
import cv2
import os

class Recorder:

	#vidWriter = None

	def __init__(self, frame_width, frame_height, fps):

		# standardize parameters
		self.fixed_Height = frame_height
		self.fixed_Width = frame_width
		self.fixed_fps = fps
		self.predefinedFilePath = "undefined"
		self.isRecording = False
		self.vidWriter = None

	# Date/Time setter and getters
	def setDisplayLabel(self):
		self.datetime4display = QDateTime.currentDateTime().toString()

	def getDisplayLabel(self):
		self.setDisplayLabel()
		return self.datetime4display

	def setCurrentTime(self):
		timeRaw = QTime.currentTime().toString(Qt.DefaultLocaleLongDate).split()
		timeDiscrete = timeRaw[0].split(':')
		self.time4processing = str(timeDiscrete[0]) + "_" + str(timeDiscrete[1]) + "_" + str(timeDiscrete[2]) + "_" + str(timeRaw[1])		

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

	def getPreDefinedFilePath(self):
		return self.predefinedFilePath

	def getRecordingStatus(self):
		return self.isRecording

	def turnOffRecording(self):
		self.isRecording = False

	def invokeRecording(self):

		'''
			Description: start recording from the camera and save it to
			Saved file format: user_defined_directory/current_date/current_time.avi
		'''
		self.setCurrentTime()
		self.setTodayDate()

		completeFolderDir = self.predefinedFilePath + '/' + self.date4processing + '/'

		print(type(completeFolderDir))
		print(type(self.time4processing))

		os.makedirs(os.path.dirname(completeFolderDir), exist_ok=True)
		completeFilePath = completeFolderDir + str(self.time4processing) + '.avi'

		if self.vidWriter == None:
			self.vidWriter = cv2.VideoWriter(completeFilePath, cv2.VideoWriter_fourcc('M','J','P','G'), self.fixed_fps, (self.fixed_Width,self.fixed_Height))
		else:
			self.vidWriter.open(completeFilePath, cv2.VideoWriter_fourcc('M','J','P','G'), self.fixed_fps, (self.fixed_Width,self.fixed_Height))

		

		if self.vidWriter.isOpened:
			self.isRecording = True
			print("VideoWriter opened successfully")
		else:
			self.isRecording = False
			print("Error! Failed to open video writer")

	def killRecorder(self):
		if self.vidWriter != None:
			self.vidWriter.release()










