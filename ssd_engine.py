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

## Object detection imports
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util


class SSD_Detector:

  def __init__(self):
    CWD_PATH = os.getcwd()
    MODEL_FOLDER = 'models'
    MODEL_NAME = 'ssd_mobilenet_v1_model'
    PATH_TO_CKPT = os.path.join(CWD_PATH, MODEL_FOLDER ,MODEL_NAME, 'frozen_inference_graph.pb')
    PATH_TO_LABELS = os.path.join(CWD_PATH, MODEL_FOLDER, MODEL_NAME, 'label_map.pbtxt')
    
    # 1 - person, 2 - dog, 3 - cat
    NUM_CLASSES = 3

    # ssd engine ready signal
    self.ready = False

    # begin load models
    try:
      self.detection_graph = tf.Graph()
      with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
              serialized_graph = fid.read()
              od_graph_def.ParseFromString(serialized_graph)
              tf.import_graph_def(od_graph_def, name='')

      self.detection_graph.as_default()
    except:
      print('Warning! Failed to load ' + MODEL_NAME + ' frozen graph file (.pb), object detection disabled') 

    try: 
      label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
      categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)

      self.category_index = label_map_util.create_category_index(categories)
      self.sess = tf.Session(graph=self.detection_graph)
      self.ready = True
    except:
      print('Warning! Failed to load ' + MODEL_NAME + ' label map (.pbtxt), object detection disabled')



  def process_image(self, image_np):
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image_np, axis=0)
        image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
        # Each box represents a part of the image where a particular object was detected.
        boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        classes = self.detection_graph.get_tensor_by_name('detection_classes:0')

        num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
        # Actual detection.
        (boxes, scores, classes, num_detections) = self.sess.run([boxes, scores, classes, num_detections],feed_dict={image_tensor: image_np_expanded})  

        # Obtain objects detected in the current frame
        objects_detected = vis_util.visualize_boxes_and_labels_on_image_array(image_np,
                                                                              np.squeeze(boxes),
                                                                              np.squeeze(classes).astype(np.int32),
                                                                              np.squeeze(scores),
                                                                              self.category_index,
                                                                              use_normalized_coordinates=True,
                                                                              line_thickness=6)

        # Get the dimension of the frame
        img_height, img_width, dim = image_np.shape

        detected_objs = []
        
        # iterate it and display on screen
        if type(objects_detected) is list:
          for obj in objects_detected:

              obj_name = obj[0]
              obj_prob = obj[1]

              display_text = obj_name + ": " + str(obj_prob)

              # TODO: make this part more scalable
              if obj_name == "person":
                  display_colour = (255,0,0) # red
                  
                  if obj_name not in detected_objs:
                    detected_objs.append(obj_name)

                  # topleft & bottomright coord of the bbox
                  tl = (int(obj[3]*img_width), int(obj[2]*img_height))
                  br = (int(obj[5]*img_width), int(obj[4]*img_height))

                  # display text coord
                  display_text_coord = (tl[0]+5,tl[1]-10)

                  cv2.putText(image_np,display_text,display_text_coord,0,0.5,display_colour)
                  cv2.rectangle(image_np,tl,br,display_colour,2)

        return image_np, detected_objs