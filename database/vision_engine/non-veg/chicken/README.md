# Chicken Meat Vision Engine

YOLOv8-based object detection module for identifying good and rotten chicken meat.

## Classes

| ID | Class |
|---:|---|
| 0 | chicken-meat-good |
| 1 | chicken-meat-rooten |

## Dataset

Source: Roboflow — Chicken Meat Detection, Version 2 (`chicken_dataset`).

Dataset split:

- Train: 2,800 images
- Valid: 80 images
- Test: 40 images
- Total: 2,920 images

The original dataset contained polygon annotations. These were converted to enclosing YOLO bounding boxes for object detection training.

The original dataset is preserved unchanged under `raw/`.

## Model

- Architecture: YOLOv8n
- Task: Object Detection
- Training epochs: 10
- Image size: 640
- Batch size: 8
- Device: CPU
- Ultralytics: 8.4.138

Final model: `models/final/chicken_yolov8n.pt`

## Results

Held-out test-set results:

- Precision: 0.991
- Recall: 1.000
- mAP@50: 0.995
- mAP@50-95: 0.986

See `MODEL_RESULTS.md` for the complete evaluation results.

## Directory Structure

```text
chicken/
├── raw/
├── processed/
├── metadata/
├── scripts/
├── models/
│   └── final/
│       └── chicken_yolov8n.pt
├── runs/
├── README.md
└── MODEL_RESULTS.md
```

## Inference

Example using the final model:

```bash
yolo detect predict \\
  model=database/vision_engine/non-veg/chicken/models/final/chicken_yolov8n.pt \\
  source=<IMAGE_PATH> \\
  imgsz=640 \\
  device=cpu
```

## Important Note

The validation and test sets are relatively small. The reported metrics are strong baseline results, but additional real-world testing is recommended before production deployment.
