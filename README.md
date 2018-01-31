### Description
DeepEye is a video surveillance application that runs on your idelling desktop computer. This project is inspired based on use cases of object detection using deep learning. There are two modes of detection; motion and object. The object detection backend uses SSD architecture and detects presence of human and pets. The code is open-source, feel free to modify for your own.

### Dependencies
- Ubuntu 16.04.3
- OpenCV 3.1
- Tensorflow r1.3
- Python 3.5
- pyQT5



### Useful Command
For training of your own dataset:
~~~~
python3 export_inference_graph.py --input_type image_tensor --pipeline_config_path training/ssd_mobilenet_v1_coco.config --trained_checkpoint_prefix training/model.ckpt-490468 --output_directory ssd_3class
~~~~
