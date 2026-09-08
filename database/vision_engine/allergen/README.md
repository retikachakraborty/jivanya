# Allergen Vision Engine

## Overview

The Allergen Vision Engine is a YOLO11n-based object detection module designed to identify food items relevant to allergen detection and food-safety analysis.

The current trained model detects 19 food-related classes.

## Model

- Architecture: YOLO11n
- Task: Object Detection
- Parameters: 2,585,857
- GFLOPs: 6.4
- Model file: models/final/allergen30_yolo11n.pt
- Framework: Ultralytics YOLO

## Classes

The model detects the following 19 classes:

1. alcohol
2. alcohol_glass
3. bread
4. bread_loaf
5. capsicum
6. cheese
7. chocolate
8. cooked_meat
9. dates
10. egg
11. eggplant
12. icecream
13. milk
14. milk_based_beverage
15. mushroom
16. non_milk_based_beverage
17. raw_meat
18. spinach
19. whole_egg_boiled

## Dataset

The model was evaluated using the matching 19-class Allergen30 test configuration located at:

processed/allergen30_before_egg_removal/data.yaml

- Test images: 427
- Test object instances: 1,144
- Number of classes: 19

## Test Performance

| Metric | Result |
|---|---:|
| Precision | 60.33% |
| Recall | 47.15% |
| mAP@50 | 51.64% |
| mAP@50-95 | 27.10% |
| Inference time | 55.6 ms/image |

## Usage

Prediction and evaluation scripts are available in the scripts directory. The trained model is stored in the models/final directory.

## Directory Structure

allergen/
├── metadata/
│   ├── classes.csv
│   └── image_manifest.csv
├── models/
│   └── final/
│       └── allergen30_yolo11n.pt
├── processed/
│   ├── allergen30/
│   └── allergen30_before_egg_removal/
├── raw/
├── runs/
├── scripts/
│   ├── clean_allergen30.py
│   ├── evaluate.py
│   ├── predict.py
│   └── train.py
├── MODEL_RESULTS.md
└── README.md

## Evaluation

The reported metrics were obtained by evaluating allergen30_yolo11n.pt against the matching 19-class test dataset using Ultralytics YOLO with 640px image size and CPU inference.
