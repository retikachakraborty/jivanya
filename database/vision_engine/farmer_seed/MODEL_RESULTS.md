# Jivanya Vision Engine — Model Results

## Overview

This document records the dataset preparation, model training, and testing results for the Jivanya Vision Engine.

The workflow followed was:

Dataset Collection → Dataset Cleaning → Dataset Preparation → Model Training → Model Testing → Real-World Testing

---

# 1. Indian Ingredients — Sequel Farmer

## Dataset

- Source: Roboflow Universe — Sequel Farmer Dataset
- Original images: 2,112
- Original classes: 43
- Task: Object detection / segmentation
- Final task: YOLO segmentation

## Dataset Preparation

The dataset was cleaned and prepared for training. Class imbalance was investigated through multiple experiments, including:

- Original dataset
- Balanced split
- Object-balanced dataset
- Oversampled dataset

The oversampled training configuration produced the best result.

## Final Model

- Architecture: YOLO11n-Seg
- Training epochs: 5
- Final model:

`models/final/indian_ingredients_yolo11n_seg.pt`

## Final Test Results

- Box mAP@50: 40.7%
- Mask mAP@50: 35.3%
- Box Recall: 59.1%

---

# 2. Indian Spices

## Dataset

- Source: Mendeley Data
- Dataset: Indian Spices Image Dataset
- Total images: 10,991
- Classes: 19
- Task: Image classification

## Dataset Split

- Training: 8,786
- Validation: 1,092
- Testing: 1,113

## Final Model

- Architecture: MobileNetV3-Small
- Input size: 160 × 160
- Training epochs: 10
- Final model:

`models/indian_spices_mobilenetv3.pth`

## Final Test Results

- Test accuracy: 97.48%
- Correct predictions: 1,085 / 1,113

---

# 3. Allergen30

## Dataset

- Source: Mendeley Data — Allergen30
- Original images: 14,524
- Original classes: 30
- Final classes: 19
- Task: Object detection

## Removed Classes

The following classes were removed:

- almond
- avocado
- blackberry
- blueberry
- pasta
- pineapple
- pistachio
- pizza
- roti
- strawberry
- tomato

## Final Dataset

- Training images: 8,423
- Validation images: 796
- Test images: 427
- Final classes: 19
- Final annotated objects: 26,905

Dataset integrity was checked successfully.

## Final Model

- Architecture: YOLO11n
- Training epochs: 10
- Image size: 320 × 320
- Batch size: 4
- Device: CPU
- Final model:

`models/final/allergen30_yolo11n.pt`

## Final Test Results

- Precision: 78.46%
- Recall: 64.50%
- mAP@50: 72.50%
- mAP@50–95: 48.95%

---

# 4. Grocery Detection

## Dataset

- Source: Roboflow Universe — Grocery Detection
- Original classes: 4
- Original classes:
  - atta
  - maida
  - suji
  - vermicelli

## Dataset Preparation

The original annotations were polygon/segmentation-style annotations.

The polygons were converted to YOLO bounding-box annotations for object detection.

The raw dataset was kept unchanged.

## 4-Class Experiment

The initial 4-class model included:

- atta
- maida
- suji
- vermicelli

The `suji` class showed unreliable detection performance.

Therefore, a 3-class version was created for the final model.

## Final Classes

- atta
- maida
- vermicelli

## Final Dataset

- Training images: 308
- Validation images: 87
- Test images: 42
- Test objects: 46

Dataset integrity was successfully verified.

## Final Model

- Architecture: YOLO11n
- Training epochs: 10
- Image size: 320 × 320
- Batch size: 4
- Device: CPU
- Final model:

`models/final/grocery_detection_yolo11n.pt`

## Final Test Results

- Precision: 59.0%
- Recall: 58.6%
- mAP@50: 49.1%
- mAP@50–95: 30.4%

### Per-Class Results

| Class | Precision | Recall | mAP@50 | mAP@50–95 |
|---|---:|---:|---:|---:|
| Atta | 65.0% | 42.2% | 50.4% | 30.2% |
| Maida | 30.0% | 57.1% | 27.9% | 19.9% |
| Vermicelli | 81.9% | 76.5% | 69.0% | 40.9% |

---

# 5. Grocery Real-World Testing

The final Grocery Detection model was tested on real-world images outside the dataset.

## Test 1 — Atta Flour

Image:

`/home/mousumi/Pictures/Atta_flour.jpg`

Detection:

- atta
- maida

The model correctly detected atta but also produced a false-positive maida detection.

Strong detections:

- maida: 63.69%
- atta: 53.46%

## Test 2 — Maida Image

Image:

`/home/mousumi/Pictures/images.jpeg`

Detection:

- maida

## Test 3 — Wheat Flour Chakki Atta

Image:

`/home/mousumi/Pictures/wheat-flour-chakki-atta-1000x1000.webp`

Detection:

- atta
- vermicelli

The model correctly detected atta but also produced a false-positive vermicelli detection.

## Real-World Testing Observation

The Grocery Detection model successfully performs inference on unseen real-world images. However, some cross-class false positives occur, particularly between visually similar grocery products.

---

# 6. Final Model Inventory

All final trained models are stored under:

`models/final/`

| Model | Task | Classes |
|---|---|---:|
| indian_ingredients_yolo11n_seg.pt | Segmentation | 43 |
| allergen30_yolo11n.pt | Object Detection | 19 |
| grocery_detection_yolo11n.pt | Object Detection | 3 |
| indian_spices_mobilenetv3.pth | Classification | 19 |

---

# 7. Training Environment

- Operating System: Ubuntu
- Python: 3.14.4
- Ultralytics: 8.4.138
- PyTorch: 2.14.0+cpu
- Hardware: 12th Gen Intel Core i5-12450H
- Training device: CPU

---

# 8. Conclusion

The dataset collection, cleaning, preparation, model training, evaluation, and initial real-world testing stages for the Jivanya Vision Engine have been completed.

The final models are saved separately from the raw datasets, and the raw datasets remain unchanged.

The Grocery Detection experiments demonstrated that removing the unreliable `suji` class improved overall recall and mAP compared with the 4-class experiment.

Further improvements can be considered later through additional real-world training data, better class balancing, augmentation, or longer training.
