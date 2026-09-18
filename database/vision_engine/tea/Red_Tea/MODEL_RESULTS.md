# Red Tea Model Results

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
| Precision | 1.000 |
| Recall | 1.000 |
| mAP50 | 0.995 |
| mAP50-95 | 0.936 |
| Inference Speed | ~37.2 ms/image |

## External Image Test

No separate real-world Red Tea image was available for external testing.

The reported metrics are from the held-out dataset test split.

## Checkpoint

`runs/detect/database/vision_engine/tea/runs/red_tea_yolov8n/weights/best.pt`

The model checkpoint is excluded from Git because model weights are ignored by the repository configuration.
