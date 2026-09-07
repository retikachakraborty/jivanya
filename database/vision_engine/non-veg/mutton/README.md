# Mutton Vision Detection

YOLOv8-based mutton detection component of Jivanya's non-vegetarian vision engine.

## Structure

- `raw/` - original downloaded dataset
- `processed/` - prepared train/validation/test dataset
- `metadata/` - dataset metadata
- `scripts/` - training, evaluation and prediction scripts
- `MODEL_RESULTS.md` - recorded model performance

Raw and processed image datasets and trained model weights are excluded from Git.

## Dataset

Roboflow Universe Mutton Dataset v2.

The original dataset contained 1,496 annotated images in the training split. A reproducible 70/20/10 train-validation-test split was created locally using random seed 42.

The original class `objects` was normalized to `mutton`.

## Model

YOLOv8n was fine-tuned for 10 epochs.

Final held-out test performance:

- Precision: 0.795
- Recall: 0.518
- mAP@50: 0.632
- mAP@50-95: 0.297

See `MODEL_RESULTS.md` for additional details.
