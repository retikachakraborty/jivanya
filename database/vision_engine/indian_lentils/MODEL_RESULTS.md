# Indian Lentils - Model Results

## Dataset

- Training images: 7,505
- Original validation images: 1,885
- Clean validation images: 1,035
- Classes: 20

The original train/validation split contained no exact SHA-256 duplicate images.

A perceptual-hash check found strong near-duplicate overlap. 850 of 1,885 original validation images had a training-image match at pHash distance <= 2.

A clean validation set was created by removing those 850 images.

Final clean split:

- Train: 7,505
- Validation: 1,035
- Classes: 20
- Clean validation images with pHash distance <= 2 to training: 0

The original dataset was not modified.

## Model

Architecture: YOLO11n Classification

Input: 224 x 224

Epochs: 10

Batch size: 16

Device: CPU

Ultralytics: 8.4.138

## Original Model Results

Model:

database/vision_engine/indian_lentils/models/final/indian_lentils_yolo11n_cls.pt

Results:

- Top-1 accuracy: 100%
- Top-5 accuracy: 100%

## Clean Model Results

Model:

database/vision_engine/indian_lentils/models/final/indian_lentils_yolo11n_cls_clean.pt

Results on the clean validation set:

- Top-1 accuracy: 100%
- Top-5 accuracy: 100%
- Misclassified images: 0
- Per-class accuracy: 100%
- Inference time: approximately 1.9 ms/image
- Model size: approximately 3.2 MB

The confusion matrix contains no off-diagonal errors.

## Evaluation Artifacts

Stored in:

database/vision_engine/indian_lentils/metadata/evaluation/

Files:

- confusion_matrix.png
- confusion_matrix_normalized.png
- val_batch0_labels.jpg
- val_batch0_pred.jpg

## Training Run

Clean training run:

database/vision_engine/indian_lentils/runs/clean_eval_10ep/

The model completed 10 training epochs.

## Interpretation

The clean validation evaluation achieved 100% Top-1 and Top-5 accuracy with zero validation errors.

This result should still be interpreted in the context of the available dataset. The clean split removes strong perceptual overlap with training images, but an independent external test set would provide a stronger measurement of real-world generalization.

## Status

Indian Lentils Vision Engine module: evaluation complete.
