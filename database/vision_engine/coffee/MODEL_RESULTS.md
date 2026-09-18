# Coffee Model Results

## Training Configuration

| Parameter | Value |
|---|---|
| Model | YOLOv8n Classification |
| Classes | 4 |
| Training images | 1,200 |
| Test images | 400 |
| Validation split | None; test used during validation |
| Epochs | 10 |
| Image size | 224x224 |
| Batch size | 16 |
| Device | CPU |

## Evaluation

| Metric | Result |
|---|---:|
| Top-1 Accuracy | 1.000 |
| Top-5 Accuracy | 1.000 |
| Inference Speed | ~2.1 ms/image |

## External Image Test

Image: `~/Downloads/coffee.jpg`

| Class | Confidence |
|---|---:|
| Dark | 0.99 |
| Light | 0.01 |
| Green | 0.00 |
| Medium | 0.00 |

This single external image is a qualitative sanity check and is not part of the reported dataset accuracy.

## Checkpoint

`runs/classify/database/vision_engine/coffee/runs/coffee_yolov8n/weights/best.pt`

The model checkpoint is excluded from Git because model weights are ignored by the repository configuration.
