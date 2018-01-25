import numpy as np
import cv2


class MotionDetector:

	def __init__(self):
		self.bgsubtractor = cv2.bgsegm.createBackgroundSubtractorMOG()
		self.firstObserv = True
		self.prob = 0
		self.motion = False

	def gaussianfilter(self,inputImg):
		return cv2.GaussianBlur(inputImg,(15,15),0)

	def medianblur(self,inputImg):
		return cv2.medianBlur(iinputImg,5)

	def threshold(self,inputImg):
		_,result = cv2.threshold(inputImg,10,255,cv2.THRESH_BINARY)

	def calculate_movement(self,inputImg):
		height, width = inputImg.shape
		area = height*width
		activepixels = cv2.countNonZero(inputImg)
		motionPercentage = (activepixels / area)*100

		if motionPercentage > 1:
			self.motion = True
		else:
			self.motion = False

	def bayesianclassifier(self):
		'''
		Bayesian Classifier
		Input Args:	boolean moved or not
		Output Args: probability of movement 
		---------------------------------------------------------------
	   	probability of motion: 0.5
	   	probability of observed motion given there is motion: 0.8
	   	probability of observed motion given there is no motion: 0.1

	   	probability of no observed motion given there is motion 0.1
		probability of no observed motion given there is no motion 0.8
		---------------------------------------------------------------
		'''
		if self.firstObserv:
			if self.motion:
				self.prob = (0.8*0.5)/0.9
			else:
				self.prob = (0.1*0.5)/0.9
			self.firstObserv = False
		else:
			if self.motion:
				self.prob = (0.8*self.prob)/( (0.8*self.prob) + 0.1*(1-self.prob))
			else:
				self.prob = (0.1*self.prob)/( (0.1*self.prob) + 0.8*(1-self.prob))

		# simple boundary setting
		if self.prob > 0.6:
			self.prob = 0.6

		if self.prob < 0.1:
			self.prob = 0.1

	def detectmotion(self, inputImg):
		self.calculate_movement(inputImg)
		return self.bayesianclassifier(self) > 0.5