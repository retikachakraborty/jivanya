# Vegetable Detection Model Results

## Dataset

Dataset: Emam Vegetable Detection v14
Format: YOLOv8 Object Detection
Classes: 24
Train images: 3962
Validation images: 380
Test images: 192
License: CC BY 4.0

## Model

Model: YOLO11n
Initial training: 3 epochs
Additional fine-tuning: 7 epochs
Image size: 640
Batch size: 8
Device: CPU

## Final Validation Metrics

- Precision: 0.617
- Recall: 0.671
- mAP@50: 0.671
- mAP@50-95: 0.530

## Final Model

`models/final/vegetables_yolo11n.pt`

## Real-World Evaluation

The model was tested using external vegetable images not taken from the training dataset.

Most tested classes were detected successfully after fine-tuning. Onion, which initially performed poorly after the first 3 epochs, improved significantly after the additional training and was successfully detected in external images.

Final retention of classes is based on both validation metrics and external real-world testing.
