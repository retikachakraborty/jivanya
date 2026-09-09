# Egg Model Results

## Model Status

A YOLO11n object-detection model has been successfully trained on the Egg dataset.

- Training performed: Yes
- Model: YOLO11n
- Training epochs: 5
- Image size: 640
- Batch size: 8
- Device: CPU
- Model weights: `models/final/egg_yolo11n.pt`
- Training run: `runs/detect/egg_yolo11n_5ep/`

## Dataset Used

The Egg dataset contains two classes:

| Class ID | Class |
|---:|---|
| 0 | egg |
| 1 | whole_egg_boiled |

### Dataset Split

| Split | Images | Labels |
|---|---:|---:|
| Train | 1,880 | 1,880 |
| Validation | 176 | 176 |
| Test | 91 | 91 |
| **Total** | **2,147** | **2,147** |

## Training Results

The best validation performance was obtained at epoch 5.

| Metric | Overall |
|---|---:|
| Precision | 85.10% |
| Recall | 79.40% |
| mAP@50 | 88.20% |
| mAP@50-95 | 65.40% |

### Per-Class Validation Results

| Class | Images | Instances | Precision | Recall | mAP@50 | mAP@50-95 |
|---|---:|---:|---:|---:|---:|---:|
| egg | 137 | 223 | 82.50% | 72.60% | 83.30% | 58.50% |
| whole_egg_boiled | 47 | 211 | 87.50% | 86.20% | 93.10% | 72.40% |

## Inference Speed

Validation inference speed for the trained model:

- Preprocessing: 1.9 ms/image
- Inference: 62.7 ms/image
- Postprocessing: 1.6 ms/image

## Training Loss

At the final epoch:

- Training box loss: 0.79827
- Training classification loss: 1.32730
- Training DFL loss: 1.57045
- Validation box loss: 1.09159
- Validation classification loss: 1.32334
- Validation DFL loss: 1.90716

## Model Files

Final trained model:

`models/final/egg_yolo11n.pt`

The original training run also contains:

`runs/detect/egg_yolo11n_5ep/weights/best.pt`

`runs/detect/egg_yolo11n_5ep/weights/last.pt`

## Training Run Artifacts

The actual training run is preserved in:

`runs/detect/egg_yolo11n_5ep/`

It contains the training configuration, results CSV, metric plots, confusion matrices, training/validation visualizations, and model weights.

## Important Evaluation Note

The metrics reported above are the model's training-run validation metrics on the 176-image validation set.

The dataset also contains a separate 91-image test set. These results should not be described as final test-set performance until the trained model is evaluated on that test set.

## Conclusion

The Egg YOLO11n model was successfully trained for 5 epochs. The best validation results reached 85.10% precision, 79.40% recall, 88.20% mAP@50, and 65.40% mAP@50-95.

The `best.pt` model is preserved as:

`models/final/egg_yolo11n.pt`

The complete real training artifacts are preserved under:

`runs/detect/egg_yolo11n_5ep/`

## Final Test-Set Evaluation

The trained YOLO11n model was evaluated on the separate 91-image test set.

| Metric | Test Result |
|---|---:|
| Precision | 82.65% |
| Recall | 77.95% |
| mAP@50 | 86.78% |
| mAP@50-95 | 63.03% |

### Per-Class Test Results

| Class | Images | Instances | Precision | Recall | mAP@50 | mAP@50-95 |
|---|---:|---:|---:|---:|---:|---:|
| egg | 68 | 100 | 72.40% | 81.00% | 86.10% | 58.60% |
| whole_egg_boiled | 24 | 87 | 92.90% | 74.90% | 87.50% | 67.40% |

### Test Inference Speed

- Preprocessing: 2.2 ms/image
- Inference: 54.2 ms/image
- Postprocessing: 1.1 ms/image

### Test Evaluation Artifact

The test evaluation output was generated at:

`runs/detect/val-4/`

## Final Conclusion

The Egg YOLO11n model was trained for 5 epochs and achieved the following final test-set performance:

- Precision: **82.65%**
- Recall: **77.95%**
- mAP@50: **86.78%**
- mAP@50-95: **63.03%**

These metrics are based on the separate 91-image test set and can be reported as the model's final test performance.
