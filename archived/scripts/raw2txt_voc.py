import json
import os
import shutil
import glob
import pandas as pd
import xml.etree.ElementTree as ET

from pprint import pprint
from pathlib import Path

# For VOC Dataset (find all cats and dogs without human)
sourceAnnoDir = "raw/annotation"
sourceTrainDir = "raw/images"

targetImgDir = "processed/data"
targetAnnoDir = "processed/labels"

def find_cats_dogs(path):
    for xml_file in glob.glob(path + '/*.xml'):
        tree = ET.parse(xml_file)
        root = tree.getroot()

        take = True
        for member in root.findall('object'):
        	if member[0].text == 'person':
        		take = False
        		break

        if take:
	        for member in root.findall('object'):
	        	writeString = ""

	        	dogs = 0
	        	cats = 0

	        	nameOfInterest = member.find('name').text

	        	if nameOfInterest == 'dog':
	        		sub = member.find('bndbox')
	        		writeString = "2 " + sub[0].text + " " + sub[1].text + " " + sub[2].text + " " + sub[3].text
	        		dogs += 1
	        	elif nameOfInterest == 'cat':
	        		sub = member.find('bndbox')
	        		writeString = "3 " + sub[0].text + " " + sub[1].text + " " + sub[2].text + " " + sub[3].text
	        		cats += 1
       			
       			if len(writeString) > 0:

       				imageName = root.find('filename').text
       				txtName = imageName[:-4] + ".txt"

       				# check and copy image file
       				filename_img = targetImgDir + '/' + "VOC2012_dataset_" + imageName
       				filepath_img = Path(filename_img)

       				if not filepath_img.exists():
       					# filename to target
       					fname_target = targetImgDir + "/" + "VOC2012_dataset_" + imageName
       					shutil.copy(os.path.join(sourceTrainDir, imageName), fname_target)

       				filename_txt = targetAnnoDir + '/' + "VOC2012_dataset_" + txtName
       				filepath_txt = Path(filename_txt)

       				if filepath_txt.exists():
       					with open(filename_txt, "a") as myfile:
       						myfile.write(writeString)
       						myfile.close()
       				else:
       					with open(filename_txt, "w") as myfile:
       						myfile.write(writeString)
       						myfile.close()

       				print("Number of Dogs/Cats: " + str(dogs) + " ," + str(cats))


def main():
    image_path = os.path.join(os.getcwd(), sourceAnnoDir)
    find_cats_dogs(image_path)


main()



