import numpy as np
import cv2


cap = cv2.VideoCapture(0)
fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
firstObserv = True
prob = 0


# filter methods
def gaussianfilter(input):
	return cv2.GaussianBlur(input,(15,15),0)

def medianblur(input):
	return cv2.medianBlur(input,5)

def threshold(input):
	_,result = cv2.threshold(input,10,255,cv2.THRESH_BINARY)
	return result

def calculate_movement(input):

	height, width = input.shape
	area = height*width
	activepixels = cv2.countNonZero(input)
	motionPercentage = (activepixels / area)*100
	return motionPercentage

def bayesianclassifier(moved):

	'''
	Bayesian Classifier:
	---------------------------------------------------------------
   	probability of motion: 0.5
   	probability of observed motion given there is motion: 0.8
   	probability of observed motion given there is no motion: 0.1

   	probability of no observed motion given there is motion 0.1
	probability of no observed motion given there is no motion 0.8
	---------------------------------------------------------------
	
	'''

	global prob
	global firstObserv

	if firstObserv:
		if moved:
			prob = (0.8*0.5)/0.9
		else:
			prob = (0.1*0.5)/0.9
		firstObserv = False
	else:
		if moved:
			prob = (0.8*prob)/( (0.8*prob) + 0.1*(1-prob))
		else:
			prob = (0.1*prob)/( (0.1*prob) + 0.8*(1-prob))

	if prob > 0.6:
		prob = 0.6

	if prob < 0.1:
		prob = 0.1

	return prob

while(1):

    ret, frame = cap.read()

    img = medianblur(frame)

    out1 = fgbg.apply(img)
    out2 = gaussianfilter(out1)
    out3 = threshold(out2)

    motion = False
    if calculate_movement(out3) > 1:
    	motion = True

    if bayesianclassifier(motion) > 0.5:
    	print("motion observed!")
    else:
    	print("no motion")


    cv2.imshow('medium', out3)

    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()