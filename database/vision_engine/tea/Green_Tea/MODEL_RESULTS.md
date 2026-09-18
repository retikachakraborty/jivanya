# Green Tea Model Results

## Training Configuration

| Parameter | Value |
|---|---|
| Model | YOLOv8n Detection |
| Classes | 1 |
| Training images | 900 |
| Validation images | 300 |
| Test images | 300 |
| Epochs | 10 |
| Image size | 640x640 |
| Batch size | 16 |
| Device | CPU |

## Held-Out Test Results

| Metric | Result |
|---|---:|
| Precision | 0.991 |
| Recall | 0.993 |
| mAP50 | 0.994 |
| mAP50-95 | 0.915 |
| Inference Speed | ~39.4 ms/image |

## External Image Test

Image: `~/Downloads/greentea.png`

The model detected 2 green-tea objects.

This single external image is a qualitative sanity check and is not included in the reported test metrics.

## Checkpoint

`runs/detect/database/vision_engine/tea/runs/green_tea_yolov8n/weights/best.pt`

The model checkpoint is excluded from Git because model weights are ignored by the repository configuration.
