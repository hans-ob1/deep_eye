from PyQt5.QtCore import QDate, QTime, QDateTime, Qt

def getDisplayLabel():

	# Description: For display of date time on the image
	# Arg:
	# return time/date in string

	datetime = QDateTime.currentDateTime()
	return datetime.toString()

def get
