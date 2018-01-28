"""
Usage:
  # From tensorflow/models/
  # Create train data:
  python generate_tfrecord.py --csv_input=data/train_labels.csv  --output_path=train.record

  # Create test data:
  python generate_tfrecord.py --csv_input=data/test_labels.csv  --output_path=test.record
"""
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import io
import pandas as pd
import tensorflow as tf

from PIL import Image
from object_detection.utils import dataset_util
from collections import namedtuple, OrderedDict


precedence_folder = 'processed/'
trainRecordList = ['imagedata_2014','imagedata_2017']
testRecordList = ['imagedata_val']

flags = tf.app.flags
flags.DEFINE_string('csv_input', 'data/bikedata.csv', 'Path to the CSV input')
flags.DEFINE_string('output_path', 'bikedata.record', 'Path to output TFRecord')
FLAGS = flags.FLAGS


# TO-DO replace this with label map
def class_text_to_int(row_label):
    if row_label == 'person':
        return 1
    elif row_label == 'bike':
        return 2
    elif row_label == 'vehicle':
        return 3
    else:
        None

def int_to_class_text(row_id):
    if row_id == 1:
        return 'pedestrian'
    elif row_id == 2:
        return 'bike'
    elif row_id == 3:
        return 'vehicle'
    elif row_id == 4:
        return 'trafficlight'
    elif row_id == 5:
        return 'stopsign'
    else:
        None

def split(df, group):
    data = namedtuple('data', ['filename', 'object'])
    gb = df.groupby(group)
    return [data(filename, gb.get_group(x)) for filename, x in zip(gb.groups.keys(), gb.groups)]


def create_tf_example(group, path):
    with tf.gfile.GFile(os.path.join(path, '{}'.format(group.filename)), 'rb') as fid:
        encoded_jpg = fid.read()
    encoded_jpg_io = io.BytesIO(encoded_jpg)
    image = Image.open(encoded_jpg_io)
    width, height = image.size

    filename = group.filename.encode('utf8')
    image_format = b'jpg'
    xmins = []
    xmaxs = []
    ymins = []
    ymaxs = []
    classes_text = []
    classes = []

    for index, row in group.object.iterrows():
        xmins.append(row['xmin'] / width)
        xmaxs.append(row['xmax'] / width)
        ymins.append(row['ymin'] / height)
        ymaxs.append(row['ymax'] / height)
        # classes_text.append(row['class'].encode('utf8'))
        # classes.append(class_text_to_int(row['class']))

        classes_text.append(int_to_class_text(row['class']).encode('utf8'))
        classes.append(row['class'])

    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(filename),
        'image/source_id': dataset_util.bytes_feature(filename),
        'image/encoded': dataset_util.bytes_feature(encoded_jpg),
        'image/format': dataset_util.bytes_feature(image_format),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
    }))
    return tf_example

'''
def main(_):

    writer = tf.python_io.TFRecordWriter(FLAGS.output_path)
    path = os.path.join(os.getcwd(), 'images')
    examples = pd.read_csv(FLAGS.csv_input)
    #examples = pd.read_csv('data_w/raccoon_labels.csv')
    grouped = split(examples, 'filename')
    for group in grouped:
        tf_example = create_tf_example(group, path)
        writer.write(tf_example.SerializeToString())

    writer.close()
    output_path = os.path.join(os.getcwd(), FLAGS.output_path)
    #output_path = os.path.join(os.getcwd(), "out.record")
    print('Successfully created the TFRecords: {}'.format(output_path))
'''

def main(_):

    trainWriter = tf.python_io.TFRecordWriter('train.record')
    testWriter = tf.python_io.TFRecordWriter('test.record')

    for trainRecord in trainRecordList: 

        print("combining " + trainRecord + " to train.record......")

        path = os.path.join(os.getcwd(), precedence_folder + trainRecord)
        examples = pd.read_csv(precedence_folder + trainRecord+'.csv')
        grouped = split(examples, 'filename')
        for group in grouped:
            tf_example = create_tf_example(group, path)
            trainWriter.write(tf_example.SerializeToString())

    trainWriter.close()
    output_train = os.path.join(os.getcwd(), "train.record")

    print('Successfully created trainRecord: {}'.format(output_train))

    for testRecord in testRecordList: 

        print("combining " + testRecord + " to test.record......")

        path = os.path.join(os.getcwd(), precedence_folder + testRecord)
        examples = pd.read_csv(precedence_folder + testRecord +'.csv')

        grouped = split(examples, 'filename')
        for group in grouped:
            tf_example = create_tf_example(group, path)
            testWriter.write(tf_example.SerializeToString())

    testWriter.close()
    output_test = os.path.join(os.getcwd(), "test.record")
    print('Successfully created testRecords: {}'.format(output_test))

if __name__ == '__main__':
    tf.app.run()
