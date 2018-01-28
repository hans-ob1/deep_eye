import json
import os
import shutil

from pprint import pprint
from pathlib import Path

# 2014 Dataset COCO
sourceAnnoDir = "raw/annotations_2014/instances_val2014.json"
sourceTrainDir = "raw/val2014"

targetImgDir = "processed/imagedata_val"
targetAnnoDir = "processed/annodata_val"

with open(sourceAnnoDir) as data_file:
	data = json.load(data_file)

# list the keys
pprint(list(data.keys()))

# categories ids
print(data['categories'])


# Map COCO Dataset to 1 - pedestrian, 2 - bikes, 3 - vehicles, 4 - trafficlight, 5 - stopsign
cat_map = {1:1, 2:2, 3:3, 4:2, 6:3, 8:3, 10:4, 13:5}

def writeFile(image_index, cat_id, x, y, w, h):
	# Arg:
	# int as input
	# str as output

	# calculate xmin, ymin, xmax, ymax
	xmin = x
	ymin = y
	xmax = x + w
	ymax = y + h

	writeStr = str(cat_id) + " " + str(xmin) + " " + str(ymin) + " " + str(xmax) + " " + str(ymax) +"\n"

	# check and copy image file
	filename_img = targetImgDir + '/' + "COCO_val2014_" +str(image_index).zfill(12) + ".jpg"
	filepath_img = Path(filename_img)
	if not filepath_img.exists():
		fname = "COCO_val2014_" + str(image_index).zfill(12) + ".jpg"  # filename to change to
		shutil.move(os.path.join(sourceTrainDir, fname), targetImgDir)

	# check and write to text file
	filename_txt = targetAnnoDir + '/' + "COCO_val2014_" + str(image_index).zfill(12) + ".txt"
	filepath_txt = Path(filename_txt)
	if filepath_txt.exists():
		with open(filename_txt, "a") as myfile:
			myfile.write(writeStr)
			myfile.close()
	else:
		with open(filename_txt, "w") as myfile:
			myfile.write(writeStr)
			myfile.close()


# statistics
pedestrian = 0
bike = 0
vehicle = 0
trafficlight = 0
stopsign = 0

# find and process [1: person, 2: bicycle, 3: car, 4: motorbike, 6: bus, 8: truck, 10: trafficlight, 13: stopsign]
for i in data['annotations']:
	if i["category_id"] == 1:
		# pedestrian
		writeFile(i["image_id"], 1, i["bbox"][0], i["bbox"][1], i["bbox"][2], i["bbox"][3])
		pedestrian += 1
	elif i["category_id"] == 2 or i["category_id"] == 4:
		# bikes
		writeFile(i["image_id"], 2, i["bbox"][0], i["bbox"][1], i["bbox"][2], i["bbox"][3])
		bike += 1
	elif i["category_id"] == 3 or i["category_id"] == 6 or i["category_id"] == 8:
		# vehicles
		writeFile(i["image_id"], 3, i["bbox"][0], i["bbox"][1], i["bbox"][2], i["bbox"][3])
		vehicle +=1
	elif i["category_id"] == 10:
		# trafficlight
		writeFile(i["image_id"], 4, i["bbox"][0], i["bbox"][1], i["bbox"][2], i["bbox"][3])
		trafficlight += 1
	elif i["category_id"] == 13:
		# stopsign
		writeFile(i["image_id"], 5, i["bbox"][0], i["bbox"][1], i["bbox"][2], i["bbox"][3])
		stopsign += 1

	print("pedestrian count: " + str(pedestrian))
	print("bikes count: " + str(bike))
	print("vehicles count: " + str(vehicle))
	print("trafficlight count: " + str(trafficlight))
	print("stopsign count: " + str(stopsign))
