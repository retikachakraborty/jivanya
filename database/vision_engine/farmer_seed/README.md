# Jivanya Vision Engine — Indian Ingredient Segmentation

## Overview

This module contains the Indian ingredient dataset and the final YOLO11n-seg model used for ingredient detection and instance segmentation.

## Dataset

- Source: Roboflow Universe — Sequel Farmer Dataset
- Images: 2,112
- Classes: 43
- Task: Instance segmentation
- License: CC BY 4.0

## Dataset Split

| Split | Images |
|---|---:|
| Training | 1,666 |
| Validation | 297 |
| Testing | 149 |
| **Total** | **2,112** |

## Dataset Preparation

The dataset was cleaned and prepared for YOLO segmentation training.

The preparation included:

- YOLO annotation validation
- Bounding-box to polygon conversion
- Segmentation annotation cleaning
- Class-distribution analysis
- Dataset balancing experiments
- Minority-class oversampling

The oversampled training configuration produced the best model performance.

## Classes

The dataset contains 43 Indian ingredient and seed-related classes.

The complete class mapping is available in:

metadata/classes.csv

## Metadata

metadata/classes.csv
metadata/image_manifest.csv

The image manifest records the split, image path, label path, and class information.

## Final Model

- Architecture: YOLO11n-seg
- Task: Instance segmentation
- Training epochs: 5
- Image size: 640 × 640
- Device: CPU

Final model:

models/final/indian_ingredients_yolo11n_seg.pt

## Final Test Results

| Metric | Result |
|---|---:|
| Box Precision | 26.2% |
| Box Recall | 59.1% |
| Box mAP@50 | 40.7% |
| Box mAP@50–95 | 30.7% |
| Mask Precision | 22.0% |
| Mask Recall | 54.3% |
| Mask mAP@50 | 35.3% |
| Mask mAP@50–95 | 20.2% |

## Inference

Example:

yolo segment predict \
model=models/final/indian_ingredients_yolo11n_seg.pt \
source=path/to/image.jpg \
imgsz=640 \
conf=0.25 \
device=cpu \
save=True

## Limitations

The dataset has significant class imbalance, particularly for chickpea.

Several minority classes contain relatively few examples, which can make their individual metrics unstable.

Oversampling improved overall performance, but additional real-world images for minority classes would likely improve generalization.

## Status

- Dataset Collection: Completed
- Dataset Cleaning: Completed
- Annotation Validation: Completed
- Class Imbalance Analysis: Completed
- Balancing Experiments: Completed
- YOLO11n-seg Training: Completed
- Model Testing: Completed
- Final Model Selection: Completed

