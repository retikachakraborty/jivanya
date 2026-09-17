# Red Tea Vision Engine

YOLOv8n object detection model for detecting red tea.

## Class

| ID | Class |
|---:|---|
| 0 | red-tea |

## Dataset

Location: `database/vision_engine/tea/Red_Tea/processed/Red_Tea/`

- Train: 900 images
- Validation: 300 images
- Test: 300 images
- Classes: 1

## Model

- Model: YOLOv8n Detection
- Image size: 640x640
- Epochs: 10
- Batch size: 16
- Device: CPU

## Held-Out Test Results

- Precision: 1.000
- Recall: 1.000
- mAP50: 0.995
- mAP50-95: 0.936
- Inference speed: approximately 37.2 ms/image

## External Test

No separate real-world Red Tea image was available for external testing.

The reported metrics are from the held-out dataset test split.

## Usage

Train:

`python database/vision_engine/tea/Red_Tea/scripts/train.py`

Evaluate:

`python database/vision_engine/tea/Red_Tea/scripts/evaluate.py`

Predict:

`python database/vision_engine/tea/Red_Tea/scripts/predict.py /path/to/image.jpg`

## Model Checkpoint

`database/vision_engine/tea/Red_Tea/runs/red_tea_yolov8n/weights/best.pt`

Model weights are excluded from Git.
