# Nuts Vision Engine

YOLOv8n image classification model for identifying ten nut classes.

## Classes

| ID | Class |
|---:|---|
| 0 | Almond |
| 1 | Brazil Nuts |
| 2 | Cashew |
| 3 | Hazelnuts |
| 4 | Macademia |
| 5 | Peanut |
| 6 | Pistachio |
| 7 | Thai Peanut |
| 8 | Vietnamian Cashew |
| 9 | Walnuts |

## Dataset

Location: `database/vision_engine/nuts/processed/`

- Train: 1,108 images
- Validation: 282 images
- Test: 352 images
- Classes: 10

The processed dataset was created from the original training split using a fixed random seed (42), with 80% of the training images assigned to training and 20% to validation.

The original dataset is preserved under `raw/`.

The processed dataset includes a `manifest.csv` documenting all 1,742 images and their corresponding class and split.

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

Image: `~/Downloads/nut_test.jpg`

Prediction:

- Walnuts: 0.98
- Vietnamian Cashew: 0.01
- Brazil Nuts: 0.00
- Cashew: 0.00
- Almond: 0.00

This was a single external-image sanity check, not a dataset accuracy measurement.

## Usage

Train:

`python database/vision_engine/nuts/scripts/train.py`

Evaluate:

`python database/vision_engine/nuts/scripts/evaluate.py`

Predict:

`python database/vision_engine/nuts/scripts/predict.py /path/to/image.jpg`

## Model Checkpoint

`runs/classify/database/vision_engine/nuts/runs/nuts_yolov8n/weights/best.pt`

Model weights are excluded from Git.
