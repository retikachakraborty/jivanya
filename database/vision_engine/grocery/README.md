# Jivanya Vision Engine — Grocery Detection

## Overview

This module contains the grocery ingredient detection dataset and the final YOLO11n detection model.

## Dataset

- Source: Roboflow Universe — Grocery Detection
- Original images: 475
- Final images: 437
- Final classes: 3
- Task: Object detection

## Dataset Split

| Split | Images |
|---|---:|
| Training | 308 |
| Validation | 87 |
| Testing | 42 |
| **Total** | **437** |
## Classes

The final dataset contains:

- atta
- maida
- vermicelli

The original dataset also contained `suji`, but it was removed because its detection performance was unreliable.

## Dataset Preparation

- YOLO annotations were validated.
- Polygon annotations were converted to YOLO bounding boxes.
- Empty annotation files were excluded.
- The unreliable `suji` class was removed from the final dataset.
## Metadata

metadata/classes.csv
metadata/image_manifest.csv

## Final Model

- Architecture: YOLO11n
- Task: Object detection
- Training epochs: 10
- Image size: 320 × 320
- Batch size: 4
- Device: CPU

Final model: models/final/grocery_detection_yolo11n.pt

## Status

- Dataset Collection: Completed
- Dataset Cleaning: Completed
- Annotation Validation: Completed
- Model Training: Completed
- Model Testing: Completed
- Final Model Selection: Completed
