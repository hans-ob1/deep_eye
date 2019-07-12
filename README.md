#### Description
DeepEye is a video surveillance application that runs on your idling desktop computer. This project is inspired from the use cases of object detection using deep learning. There are two modes of detection; motion and objects. The object detection backend uses SSD architecture and detects presence of human and pets. The code base is open-sourced, feel free to modify for your own.

#### Screenshots
Screenshot 1                |  Screenshot 2              |    Screenshot 3 
:-------------------------:|:-------------------------:|:-------------------------:
![](https://raw.githubusercontent.com/khaixcore/deep_eye/master/screenshots/screenshot_1.png)  |  ![](https://raw.githubusercontent.com/khaixcore/deep_eye/master/screenshots/screenshot_2.png) | ![](https://raw.githubusercontent.com/khaixcore/deep_eye/master/screenshots/screenshot_3.png)

Screenshot 4                |  Screenshot 5              |    Screenshot 6
:-------------------------:|:-------------------------:|:-------------------------:
![](https://raw.githubusercontent.com/khaixcore/deep_eye/master/screenshots/screenshot_4.png)  |  ![](https://raw.githubusercontent.com/khaixcore/deep_eye/master/screenshots/screenshot_5.png) | ![](https://raw.githubusercontent.com/khaixcore/deep_eye/master/screenshots/screenshot_6.png)


#### Dependencies (Tested on)
- Ubuntu 16.04.3
- OpenCV 3.1
- Tensorflow r1.3
- Python 3.5
- pyQT5
- virtualenv (recommended)


#### Additional information
- Requires a CUDA ready GPU, Cuda driver and cuDNN based requirement of Tensorflow
- The frozen model in models/ssd_mobilenet_v1_model is trained on modified coco dataset, consist of human, cat and dogs.

#### Usage Instruction
After you get the dependencies, run the following cmd
~~~
python3 interface.py
~~~

#### Useful Command
You can perform your own training using [google object detection api](https://github.com/tensorflow/models/tree/master/research/object_detection). The following command is useful for training your own model and export to frozen model.

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
