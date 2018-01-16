# playback player object

import queue
import threading
import cv2

playTimer = 30
video_running = False

def imageStreamer(fName, qVideo, width, height, fps):
	global playTimer

	vidcap = cv2.VideoCapture(fName)
	vidcap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
	vidcap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
	
	fps = vidcap.get(cv2.CAP_PROP_FPS)		#as of OpenCV 3.2
	frame_number = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
	videotime = frame_number/fps

	print(videotime)

	if not vidcap.isOpened(): 
		print ("Unable to Open File")
	
	while (vidcap.isOpened() and video_running):
		ret, frame = vidcap.read()
		#qVideo.put(frame)

		# print("Debug Msg: Video Player Success!")

		cv2.waitKey(playTimer)

	print("thread killed")


class Player:

	video_thread = None
	qVideo = queue.Queue()

	def launchVideo(self,filename):
		global video_running
		video_running = True
		self.video_thread = threading.Thread(target=imageStreamer, args = (filename, self.qVideo, 1280, 720, 60))
		self.video_thread.start()

	def togglePlayer(self,play):
		global playTimer

		if (play):
			playTimer = 30
		else:
			playTimer = 0

	def retrieveFrame(self):
		frameGet = self.qVideo.get()

		if frameGet:
			print ("Frame Acquired")
			
		return frameGet

	def killPlayer(self):
		global video_running
		video_running = False
		video_thread = None



