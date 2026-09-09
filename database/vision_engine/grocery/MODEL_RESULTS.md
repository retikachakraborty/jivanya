# Jivanya Vision Engine — Grocery Detection Model Results

## Overview

This document records the dataset preparation, training, and evaluation results for the Grocery Detection model.

## Dataset

- Source: Roboflow Universe — Grocery Detection
- Original classes: atta, maida, suji, vermicelli
- Final classes: atta, maida, vermicelli
- Original images: 475
- Final images: 437
- Task: Object detection

## Dataset Split

| Split | Images |
|---|---:|
| Training | 308 |
| Validation | 87 |
| Testing | 42 |
| **Total** | **437** |

## Dataset Preparation

- Polygon annotations were converted to YOLO bounding boxes.
- Empty annotation files were excluded.
- The `suji` class was removed because its detection performance was unreliable.
- The final dataset contains 3 classes.

## Training Configuration

- Model: YOLO11n
- Epochs: 10
- Image size: 320 × 320
- Batch size: 4
- Device: CPU
## Final Model

models/final/grocery_detection_yolo11n.pt

## Final Test Results

| Metric | Result |
|---|---:|
| Precision | 59.0% |
| Recall | 58.6% |
| mAP@50 | 49.1% |
| mAP@50–95 | 30.4% |

## Per-Class Results

| Class | Precision | Recall | mAP@50 | mAP@50–95 |
|---|---:|---:|---:|---:|
| Atta | 65.0% | 42.2% | 50.4% | 30.2% |
| Maida | 30.0% | 57.1% | 27.9% | 19.9% |
| Vermicelli | 81.9% | 76.5% | 69.0% | 40.9% |
