"""
In this section, we are going to create an opencv video streamer

Author: Khai
Website: https://haixun00.github.io/
Last edited: August 2017

Reference: http://benhoff.net/face-detection-opencv-pyqt.html
"""

import sys
from os import path

import cv2
import numpy as np

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui

class RecordVideo(QtCore.QObject):
	image_data = QtCore.pyqtSignal(np.ndarray)

	def __init__(self, camera_port=0, parent=None):
		super().__init__(parent)
		self.camera = cv2.VideoCapture(camera_port)
		self.timer = QtCore.QBasicTimer()

	def image_data_slot(self, image_data):

		self.image = self.get_qimage(image_data)

		if self.image.size() != self.size():
			self.setFixedSize(self.image.size())

		self.update()


	def start_recording(self):
		self.timer.start(0, self)
	
	def timerEvent(self, event):
		if (event.timerId() != self.timer.timerId()):
			return

		read, image = self.camera.read()
		if read:
			self.image_ready.emit(image)

class MainWidget(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)

		# TODO: set video port
		self.record_video = RecordVideo()
		self.run_button = QtWidgets.QPushButton('Start')

		# Connect the image data signal and slot together
		#image_data_slot = self.face_detection_widget.image_data_slot
		#self.record_video.image_data.connect(image_data_slot)

		image_data_slot = self.record_video.image_data_slot
		self.record_video.image_data.connect(image_data_slot)

		# Connect the run button to the start recording slot
		self.run_button.clicked.connect(self.record_video.start_recording)

		# Create and set the layout
		layout = QtWidgets.QVBoxLayout()
		layout.addWidget(self.run_button)

		self.setLayout(layout)

def main():
	app = QtWidgets.QApplication(sys.argv)

	main_window = QtWidgets.QMainWindow()
	main_widget = MainWidget()
	main_window.setCentralWidget(main_widget)
	main_window.show()
	sys.exit(app.exec_())

if __name__ == '__main__':
    main()