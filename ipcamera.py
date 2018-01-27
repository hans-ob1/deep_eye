import urllib.request
import cv2
import numpy as np

'''
Note for IP camera:
Different supplier has different video feed url, look up on zoneminderwiki
for Dlink ip cameras: https://wiki.zoneminder.com/D-Link#DCS-5222L

'''

DLINK_DCS_5222L_URL = "http://admin:asd123@192.168.0.103:80/video/mjpg.cgi"
cap = cv2.VideoCapture()
cap.open(DLINK_DCS_5222L_URL)

while cap.isOpened():

	ret,img = cap.read()

	cv2.imshow('test',img)

	if ord('q') == cv2.waitKey(10):
		exit(0)q