# Nuts Model Results

## Training Configuration

| Parameter | Value |
|---|---|
| Model | YOLOv8n Classification |
| Classes | 10 |
| Training images | 1,390 |
| Test images | 352 |
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

Image: `~/Downloads/nut_test.jpg`

| Class | Confidence |
|---|---:|
| Walnuts | 0.98 |
| Vietnamian Cashew | 0.01 |
| Brazil Nuts | 0.00 |
| Cashew | 0.00 |
| Almond | 0.00 |

This single external image is a qualitative sanity check and is not part of the reported dataset accuracy.

## Checkpoint

`runs/classify/database/vision_engine/nuts/runs/nuts_yolov8n/weights/best.pt`

The model checkpoint is excluded from Git because model weights are ignored by the repository configuration.
