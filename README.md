### Description
This package uses google object detection api SSD mobilenetv1 model to detect and track obstacles from a live camera feed. I extracted the 5 classes data information (person, bike, vehicle, stopsign and trafficlight) from COCO dataset and trained a sample for road obstacle detection.

### Environment Setup
- Ubuntu 16.04.3
- OpenCV 3.1
- Tensorflow r1.3
- Python 3.5

### Useful Command
Frozen trained model:
~~~~
python3 export_inference_graph.py --input_type image_tensor --pipeline_config_path training/ssd_mobilenet_v1_coco.config --trained_checkpoint_prefix training/model.ckpt-490468 --output_directory ssd_3class
~~~~
