# Coffee Vision Engine

YOLOv8n image classification model for four coffee classes.

## Classes

| ID | Class |
|---:|---|
| 0 | Dark |
| 1 | Green |
| 2 | Light |
| 3 | Medium |

## Dataset

Location: `database/vision_engine/coffee/processed/`

- Train: 960 images
- Validation: 240 images
- Test: 400 images
- Classes: 4

The processed dataset was created from the original training split using a fixed random seed (42), with 80% of the training images assigned to training and 20% to validation.

The original dataset is preserved under `raw/`.

The processed dataset includes a `manifest.csv` documenting all 1,600 images and their corresponding class and split.

## Model

- Model: YOLOv8n Classification
- Image size: 224x224
- Epochs: 10
- Batch size: 16
- Device: CPU

## Results

- Top-1 accuracy: 1.000
- Top-5 accuracy: 1.000
- Inference speed: approximately 2.1 ms/image

## External Test

Image: `~/Downloads/coffee.jpg`

Prediction:

- Dark: 0.99
- Light: 0.01
- Green: 0.00
- Medium: 0.00

This was a single external-image sanity check, not a dataset accuracy measurement.

## Usage

Train:

`python database/vision_engine/coffee/scripts/train.py`

Evaluate:

`python database/vision_engine/coffee/scripts/evaluate.py`

Predict:

`python database/vision_engine/coffee/scripts/predict.py /path/to/image.jpg`

## Model Checkpoint

`runs/classify/database/vision_engine/coffee/runs/coffee_yolov8n/weights/best.pt`

Model weights are excluded from Git.
