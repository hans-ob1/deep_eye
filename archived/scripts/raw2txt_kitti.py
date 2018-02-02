import json
import os
import shutil

from pprint import pprint
from pathlib import Path

# For KITTI Dataset
sourceAnnoDir = "raw/annotations"
sourceTrainDir = "raw/images"

targetImgDir = "processed/data"
targetAnnoDir = "processed/labels"

'''
#Values    Name      Description
----------------------------------------------------------------------------
   1    type         Describes the type of object: 'Car', 'Van', 'Truck',
                     'Pedestrian', 'Person_sitting', 'Cyclist', 'Tram',
                     'Misc' or 'DontCare'
   1    truncated    Float from 0 (non-truncated) to 1 (truncated), where
                     truncated refers to the object leaving image boundaries
   1    occluded     Integer (0,1,2,3) indicating occlusion state:
                     0 = fully visible, 1 = partly occluded
                     2 = largely occluded, 3 = unknown
   1    alpha        Observation angle of object, ranging [-pi..pi]
   4    bbox         2D bounding box of object in the image (0-based index):
                     contains left, top, right, bottom pixel coordinates
   3    dimensions   3D object dimensions: height, width, length (in meters)
   3    location     3D object location x,y,z in camera coordinates (in meters)
   1    rotation_y   Rotation ry around Y-axis in camera coordinates [-pi..pi]
   1    score        Only for results: Float, indicating confidence in
                     detection, needed for p/r curves, higher is better.
'''
def writeFile(fname, cat_id, xmin, ymin, xmax, ymax):
	# Arg:
	# int as input
	# str as output

	writeStr = str(cat_id) + " " + str(xmin) + " " + str(ymin) + " " + str(xmax) + " " + str(ymax) +"\n"

	rawName = fname[:-4]

	# check and copy image file
	filename_img = targetImgDir + '/' + rawName + ".png"
	filepath_img = Path(filename_img)
	if not filepath_img.exists():
		# filename from original
		fname_img = rawName + ".png" # filename to change to
		# filename to target
		fname_target = targetImgDir + "/" + "Kitti_dataset_" + rawName + ".png"
		shutil.copy(os.path.join(sourceTrainDir, fname_img), fname_target)

	# check and write to text file
	filename_txt = targetAnnoDir + '/' + "Kitti_dataset_" + fname
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
person = 0


# main script
raw_anno = os.listdir(sourceAnnoDir)

for f_name in raw_anno:
	complete_path = sourceAnnoDir + "/" + f_name
	with open(complete_path) as fd:
		print("Writing " + f_name + ": ")
		content = fd.readlines()
		content = [x.strip('\n') for x in content]
		for i in content:
			sub = i.split()

			# check for humans
			if sub[0] == "Pedestrian" or sub[0] == "Person_sitting" or sub[0] == "Cyclist":

				# obtain left, top, right and btm coordinates
				left = float(sub[4])
				top = float(sub[5])
				right = float(sub[6])
				btm = float(sub[7])

				print("1" + " " + str(left) + " " + str(top) + " " + str(right) + " " + str(btm))
				writeFile(f_name, 1, left, top, right, btm)
		




