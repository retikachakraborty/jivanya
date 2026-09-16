# Indian Lentils Vision Engine

## Overview

This module contains the dataset, trained models, evaluation results, and supporting artifacts for Indian lentil ingredient classification.

The classification model uses YOLO11n Classification and recognizes 20 ingredient classes.

## Dataset

Original dataset:

- Training images: 7,505
- Validation images: 1,885
- Classes: 20

Dataset location:

database/vision_engine/indian_lentils/processed/

The processed dataset contains:

- Training images: 7,505
- Clean validation images: 1,035

The clean validation split was created by removing 850 strongly matching images from the original 1,885-image validation set based on pHash analysis.

## Data Quality

The original train/validation split was checked for exact duplicate images using SHA-256 hashing.

Result:

- Exact cross-split duplicates: 0

A perceptual-hash (pHash) analysis was also performed.

Result:

- Validation images with pHash distance <= 2 to a training image: 850
- Original validation images: 1,885

To reduce evaluation leakage, those 850 strongly matching validation images were removed from the evaluation set.

Clean validation set:

- Training images: 7,505
- Validation images: 1,035
- Classes: 20
- Strong pHash matches remaining: 0

The original dataset was not modified.

## Model

Architecture:

YOLO11n Classification

Configuration:

- Image size: 224 x 224
- Epochs: 10
- Batch size: 16
- Device: CPU
- Ultralytics: 8.4.138

## Models

Original validation model:

database/vision_engine/indian_lentils/models/final/indian_lentils_yolo11n_cls.pt

Clean evaluation model:

database/vision_engine/indian_lentils/models/final/indian_lentils_yolo11n_cls_clean.pt

## Results

Original validation:

- Top-1 accuracy: 100%
- Top-5 accuracy: 100%

Clean validation:

- Top-1 accuracy: 100%
- Top-5 accuracy: 100%
- Misclassified images: 0
- Per-class accuracy: 100%
- Inference time: approximately 1.9 ms/image
- Model size: approximately 3.2 MB

The clean validation confusion matrix contains no off-diagonal errors.

Detailed results are documented in:

MODEL_RESULTS.md

## Evaluation Artifacts

Location:

database/vision_engine/indian_lentils/metadata/evaluation/

Artifacts:

- confusion_matrix.png
- confusion_matrix_normalized.png
- val_batch0_labels.jpg
- val_batch0_pred.jpg

## Directory Structure

```text
indian_lentils/
├── processed/
│   ├── train/
│   └── val/
├── models/
│   └── final/
├── metadata/
│   └── evaluation/
├── README.md
├── MODEL_RESULTS.md
└── evaluation_results.json
