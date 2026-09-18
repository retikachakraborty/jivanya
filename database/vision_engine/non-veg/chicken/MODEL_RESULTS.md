# Chicken Meat Detection — Model Results

## Model

- Architecture: YOLOv8n
- Task: Object Detection
- Framework: Ultralytics
- Ultralytics version: 8.4.138
- Training epochs: 10
- Image size: 640
- Batch size: 8
- Device: CPU
- Pretrained weights: `yolov8n.pt`

## Dataset

Source: Roboflow — Chicken Meat Detection, Version 2 (`chicken_dataset`)

Classes:

- `0`: chicken-meat-good
- `1`: chicken-meat-rooten

Dataset split:

| Split | Images | Labels | Annotations |
|---|---:|---:|---:|
| Train | 2,800 | 2,800 | 2,808 |
| Valid | 80 | 80 | 81 |
| Test | 40 | 40 | 40 |
| Total | 2,920 | 2,920 | 2,929 |

Class distribution after processing:

| Class | Annotations |
|---|---:|
| chicken-meat-good | 1,423 |
| chicken-meat-rooten | 1,506 |

## Annotation Processing

The original Roboflow dataset contained:

- 2,918 polygon annotations
- 11 bounding-box annotations
- 0 invalid annotations

For YOLOv8 object detection training:

- Polygon annotations were converted to their enclosing bounding boxes.
- Existing YOLO bounding-box annotations were preserved.
- The original `raw/` dataset was left untouched.
- The processed detection dataset is stored under `processed/`.

## Validation Results

Best checkpoint validation results:

| Class | Precision | Recall | mAP@50 | mAP@50-95 |
|---|---:|---:|---:|---:|
| All | 0.998 | 0.986 | 0.985 | 0.981 |
| chicken-meat-good | 0.998 | 1.000 | 0.995 | 0.988 |
| chicken-meat-rooten | 0.998 | 0.972 | 0.975 | 0.975 |

## Held-Out Test Results

The final `best.pt` checkpoint was evaluated on the 40-image test set.

| Class | Precision | Recall | mAP@50 | mAP@50-95 |
|---|---:|---:|---:|---:|
| All | 0.991 | 1.000 | 0.995 | 0.986 |
| chicken-meat-good | 0.997 | 1.000 | 0.995 | 0.982 |
| chicken-meat-rooten | 0.985 | 1.000 | 0.995 | 0.990 |

## Inference Speed

Test evaluation reported approximately:

- Preprocess: 1.9 ms/image
- Inference: 40.2 ms/image
- Postprocess: 1.1 ms/image

## Final Model

Packaged model:

`models/final/chicken_yolov8n.pt`

The model is a YOLOv8n detection model trained to detect:

1. Good chicken meat
2. Rotten chicken meat

## Notes

The validation and test sets are relatively small (80 and 40 images respectively). Therefore, the reported metrics are strong baseline results but should not be interpreted as a definitive measure of real-world performance.
