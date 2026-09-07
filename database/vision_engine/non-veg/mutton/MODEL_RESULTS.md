# Mutton Detection Model Results

## Dataset

- Source: Roboflow Universe Mutton Dataset v2
- Format: YOLOv8 object detection
- License: CC BY 4.0
- Original images: 1,496
- Original split: 1,496 train, 0 validation, 0 test
- Class renamed from `objects` to `mutton`

## Prepared Dataset

The original dataset was reproducibly split using random seed 42.

- Training images: 1,047
- Validation images: 299
- Test images: 150
- Total bounding boxes: 2,229
- Classes: 1 (`mutton`)

## Training

- Model: YOLOv8n
- Pretrained weights: yolov8n.pt
- Epochs: 10
- Image size: 640
- Batch size: 16

## Validation Results

- Precision: 0.735
- Recall: 0.505
- mAP@50: 0.590
- mAP@50-95: 0.262

## Test Results

The best model was evaluated on the held-out 150-image test set.

- Precision: 0.795
- Recall: 0.518
- mAP@50: 0.632
- mAP@50-95: 0.297

Visual inspection of the held-out test predictions showed that most mutton instances were detected, although some instances were missed.

## Model Weights

The trained `best.pt` and other generated model artifacts are excluded from Git because model weights are covered by the repository `.gitignore`.
