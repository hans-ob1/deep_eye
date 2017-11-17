# Obstacle detection/tracking using Google Object Detection API
This package uses google object detection api SSD model to detect and track obstacles from a live camera feed. Pre-trained frozen model is localled inside /object_detection/ssd_3class folder.

### Useful Command
python3 export_inference_graph.py --input_type image_tensor --pipeline_config_path training/ssd_mobilenet_v1_coco.config --trained_checkpoint_prefix training/model.ckpt-490468 --output_directory ssd_3class
