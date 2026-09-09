# Jivanya Fruit Detection Engine

The fruit detection component of the Jivanya Vision Engine uses
YOLO11n to identify common fruits from images.

## Supported Classes

- Apple
- Banana
- Grape
- Orange
- Pineapple
- Watermelon

## Structure

- `raw/` - original downloaded fruit dataset
- `processed/` - final training-ready fruit dataset used for YOLO training
- `metadata/` - class information and image manifest
- `models/final/` - final trained model
- `scripts/` - training, evaluation and prediction scripts
- `runs/` - local training/evaluation outputs
- `test_images/` - local external test images (Git ignored)

## Dataset

The fruit detection dataset contains 8,479 annotated images:

- Train: 7,108
- Validation: 914
- Test: 457

Total annotated bounding boxes: 36,925.

## Model

Architecture: YOLO11n

Final model:

`models/final/fruits_yolo11n.pt`

## Final Validation Results

- Precision: 0.614
- Recall: 0.435
- mAP@50: 0.477
- mAP@50-95: 0.313

The model was additionally tested on external real-world fruit
images before being selected as the final checkpoint.

## Environment

The fruit engine uses the shared Jivanya Python virtual
environment located at the project root:

`.venv/`

A separate virtual environment is intentionally not maintained
inside this directory.
