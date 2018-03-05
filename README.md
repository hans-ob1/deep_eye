#### Description
DeepEye is a video surveillance application that runs on your idelling desktop computer. This project is inspired based on use cases of object detection using deep learning. There are two modes of detection; motion and object. The object detection backend uses SSD architecture and detects presence of human and pets. The code base is shared, feel free to modify for your own.

#### Screenshots
Screenshot 1                |  Screenshot 2              |    Screenshot 3 
:-------------------------:|:-------------------------:|:-------------------------:
![](https://khaixcore.github.io/img/project/deepcam/screenshot_1.png)  |  ![](https://khaixcore.github.io/img/project/deepcam/screenshot_2.png) | ![](https://khaixcore.github.io/img/project/deepcam/screenshot_3.png)

Screenshot 4                |  Screenshot 5              |    Screenshot 6
:-------------------------:|:-------------------------:|:-------------------------:
![](https://khaixcore.github.io/img/project/deepcam/screenshot_4.png)  |  ![](https://khaixcore.github.io/img/project/deepcam/screenshot_5.png) | ![](https://khaixcore.github.io/img/project/deepcam/screenshot_6.png)


#### Dependencies
- Ubuntu 16.04.3
- OpenCV 3.1
- Tensorflow r1.3
- Python 3.5
- pyQT5


#### Additional information
The frozen model in models/ssd_mobilenet_v1_model is trained on modified coco dataset, consist of human, cat and dogs. You can perform your own training using google object detection api. 

#### Useful Command
For training of your own dataset:
~~~~
python3 train.py \
         --logtostderr \
         --train_dir=training/ \
         --pipeline_config_path=training/ssd_mobilenet_v1_pets.config
~~~~

For exporting to frozen model
~~~~
python3 export_inference_graph.py \
        --input_type image_tensor \
        --pipeline_config_path training/ssd_mobilenet_v1_coco.config \
        --trained_checkpoint_prefix training/model.ckpt-490468 \
        --output_directory ssd_3class
~~~~
