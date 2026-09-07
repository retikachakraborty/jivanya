# Jivanya Vegetable Detection Engine

This module contains the vegetable object-detection component of Jivanya.

## Dataset

Primary dataset:

- Emam Vegetable Detection Dataset v14
- YOLOv8 object-detection format
- 24 classes
- 4534 images
- CC BY 4.0

## Structure

- `raw/` — original downloaded dataset
- `processed/` — cleaned/final datasets if needed
- `metadata/` — class metadata and image manifest
- `models/final/` — final trained model
- `scripts/` — preparation, prediction and evaluation utilities
- `runs/` — YOLO training results
- `test_images/` — external real-world test images

## Final Model

`models/final/vegetables_yolo11n.pt`

## Metrics

- Precision: 0.617
- Recall: 0.671
- mAP@50: 0.671
- mAP@50-95: 0.530
