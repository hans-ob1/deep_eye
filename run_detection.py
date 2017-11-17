import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile

from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image

import cv2

# cam resolution (720p)
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

## Object detection imports
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

# set capture parameter camera to 720p
cap = cv2.VideoCapture(0)
ret = cap.set(3,FRAME_WIDTH);
ret = cap.set(4,FRAME_HEIGHT);

# Path to frozen detection graph. This is the actual model that is used for the object detection.
CWD_PATH = os.getcwd()
MODEL_NAME = 'ssd_3class'
PATH_TO_CKPT = os.path.join(CWD_PATH, 'object_detection', MODEL_NAME, 'frozen_inference_graph.pb')

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join(CWD_PATH, 'object_detection', MODEL_NAME, 'detection_label_map.pbtxt')

# num of classes
NUM_CLASSES = 3

detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.GraphDef()
  with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
    serialized_graph = fid.read()
    od_graph_def.ParseFromString(serialized_graph)
    tf.import_graph_def(od_graph_def, name='')


label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)


# Detection Part
with detection_graph.as_default():
  with tf.Session(graph=detection_graph) as sess:
    while True:
      ret, image_np = cap.read()
      # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
      image_np_expanded = np.expand_dims(image_np, axis=0)
      image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
      # Each box represents a part of the image where a particular object was detected.
      boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
      # Each score represent how level of confidence for each of the objects.
      # Score is shown on the result image, together with the class label.
      scores = detection_graph.get_tensor_by_name('detection_scores:0')
      classes = detection_graph.get_tensor_by_name('detection_classes:0')

      num_detections = detection_graph.get_tensor_by_name('num_detections:0')
      # Actual detection.
      (boxes, scores, classes, num_detections) = sess.run([boxes, scores, classes, num_detections],feed_dict={image_tensor: image_np_expanded})


      # Obtain objects detected in the current frame
      objects_detected = vis_util.visualize_boxes_and_labels_on_image_array(image_np,
                                                                            np.squeeze(boxes),
                                                                            np.squeeze(classes).astype(np.int32),
                                                                            np.squeeze(scores),
                                                                            category_index,
                                                                            use_normalized_coordinates=True,
                                                                            line_thickness=6)

      # Get the dimension of the frame
      img_height, img_width, dim = image_np.shape
      
      # iterate it and display on screen
      if type(objects_detected) is list:
        for obj in objects_detected:

            obj_name = obj[0]
            obj_prob = obj[1]

            display_text = obj_name + ": " + str(obj_prob)

            # TODO: make this part more scalable
            if obj_name == "person":
                display_colour = (255,0,0) # red 
            elif obj_name == "bike":
                display_colour = (0,0,255) # blue
            else:
                display_colour = (0,255,0) # green

            # topleft & bottomright coord of the bbox
            tl = (int(obj[3]*img_width), int(obj[2]*img_height))
            br = (int(obj[5]*img_width), int(obj[4]*img_height))

            # display text coord
            display_text_coord = (tl[0]+5,tl[1]-10)

            cv2.putText(image_np,display_text,display_text_coord,0,0.5,display_colour)
            cv2.rectangle(image_np,tl,br,display_colour,2)

      cv2.imshow('Detection Result', image_np)
      if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
 