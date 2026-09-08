# Fish Model Results

## Model Status

A YOLO11n object-detection model was trained on the Fish dataset.

- Training performed: Yes
- Completed epochs: 9
- Model: YOLO11n
- Best training run: `fish_yolo11n_10ep-3`
- Best weights: `models/final/best.pt`
- Last weights: `models/final/last.pt`
- Training results: `runs/detect/fish_yolo11n_10ep-3/results.csv`

## Dataset Used

The Fish dataset contains 10 classes:

| Class ID | Class |
|---:|---|
| 0 | Bangus |
| 1 | Big-Head-Carp |
| 2 | Black-Spotted-Barb |
| 3 | Catfish |
| 4 | Climbing-Perch |
| 5 | Fourfinger-Threadfin |
| 6 | Freshwater-Eel |
| 7 | Glass-Perchlet |
| 8 | Goby |
| 9 | Gold-Fish |

## Dataset Split

| Split | Images | Labels |
|---|---:|---:|
| Train | 1,670 | 1,670 |
| Validation | 476 | 476 |
| Test | 238 | 238 |
| **Total** | **2,384** | **2,384** |

## Training Results

Metrics recorded at the final completed epoch (epoch 9) of `fish_yolo11n_10ep-3`:

| Metric | Value |
|---|---:|
| Precision | 78.80% |
| Recall | 80.74% |
| mAP@50 | 84.57% |
| mAP@50-95 | 57.65% |

## Training Loss at Epoch 9

| Loss | Value |
|---|---:|
| Train Box Loss | 0.79827 |
| Train Classification Loss | 1.32730 |
| Train DFL Loss | 1.57045 |
| Validation Box Loss | 1.09159 |
| Validation Classification Loss | 1.32334 |
| Validation DFL Loss | 1.90716 |

## Model Files

The trained model weights are stored in:

```text
models/final/best.pt
models/final/last.pt

The original training run is preserved in:
runs/detect/fish_yolo11n_10ep-3/

## Dataset Source

The original Fish dataset is stored in:
raw/fish_dataset/

## Notes

The metrics above are training/validation metrics recorded in the YOLO training results.csv.

A separate test-set evaluation should be performed before reporting these values as final test performance.

## Conclusion

The Fish dataset is organized with the original dataset in raw/, the processed dataset in processed/, metadata in metadata/, trained weights in models/, training outputs in runs/detect/, and training/evaluation scripts in scripts/.
