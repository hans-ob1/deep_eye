# Description
Obstacle detection and tracking is important for a autonomous vehicle navigation. This package uses google object detection api SSD model to detect and track obstacles from a live camera feed. I have pre-trained a model to detect 3 classes (person, bike and car), its located inside /object_detection/ssd_3class folder.

### Useful Command
python3 export_inference_graph.py --input_type image_tensor --pipeline_config_path training/ssd_mobilenet_v1_coco.config --trained_checkpoint_prefix training/model.ckpt-490468 --output_directory ssd_3class
