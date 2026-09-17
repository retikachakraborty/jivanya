# Green Tea Vision Engine

YOLOv8n object detection model for detecting green tea.

## Class

| ID | Class |
|---:|---|
| 0 | green-tea |

## Dataset

Location: `database/vision_engine/tea/Green_Tea/processed/Green_Tea/`

- Train: 900 images
- Validation: 300 images
- Test: 300 images
- Class: green-tea

## Model

- Model: YOLOv8n Detection
- Image size: 640x640
- Epochs: 10
- Batch size: 16
- Device: CPU

## Test Results

- Precision: 0.991
- Recall: 0.993
- mAP50: 0.994
- mAP50-95: 0.915
- Inference speed: approximately 39.4 ms/image

## External Test

Image: `~/Downloads/greentea.png`

The model detected 2 green-tea objects.

This external image is a qualitative sanity check and is not part of the reported test metrics.

## Usage

Train:

`python database/vision_engine/tea/Green_Tea/scripts/train.py`

Evaluate:

`python database/vision_engine/tea/Green_Tea/scripts/evaluate.py`

Predict:

`python database/vision_engine/tea/Green_Tea/scripts/predict.py /path/to/image.jpg`

## Model Checkpoint

`database/vision_engine/tea/Green_Tea/runs/green_tea_yolov8n/weights/best.pt`

Model weights are excluded from Git.
