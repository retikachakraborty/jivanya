# Jivanya Vision Engine — Indian Ingredients

## Overview

The **Jivanya Vision Engine** is the dataset preparation and machine-learning component of the **Jivanya** project.

This module is responsible for the complete computer-vision pipeline:

* Dataset collection and organization
* Dataset cleaning and preprocessing
* Annotation processing
* Dataset and class-distribution analysis
* Class-imbalance analysis
* Dataset balancing experiments
* Model training
* Model evaluation and testing
* Model selection
* Image inference and real-world testing

Four datasets are currently used in the Vision Engine. Different models are used depending on the computer-vision task.

## Dataset and Model Summary

| Dataset               | Task                                     | Original Classes | Final Classes | Model             |
| --------------------- | ---------------------------------------- | ---------------: | ------------: | ----------------- |
| **Sequel Farmer**     | Object Detection + Instance Segmentation |               43 |            43 | YOLO11n-seg       |
| **Indian Spices**     | Image Classification                     |               19 |            19 | MobileNetV3-Small |
| **Allergen30**        | Object Detection                         |               30 |            19 | YOLO11n           |
| **Grocery Detection** | Object Detection                         |                4 |             3 | YOLO11n           |

### Model Selection

The Vision Engine uses different models according to the requirements of each dataset:

* **YOLO11n-seg** — used when both object localization and instance segmentation are required.
* **YOLO11n** — used for object detection using bounding boxes.
* **MobileNetV3-Small** — used for image classification when the goal is to identify the main spice category in an image.

Therefore, the **Indian Spices model is a classification model, not an object-detection model**.

---

# 1. Datasets Used

## 1.1 Sequel Farmer Dataset

The Indian ingredient detection and segmentation task uses the **Sequel Farmer Dataset** from Roboflow Universe.

**Dataset source:**

https://universe.roboflow.com/ayushi-beutb/sequel-farmer-cxwdj

The Roboflow project provides dataset version 1 containing **2,112 images**, which is the version used for this project.

For this project, the downloaded dataset contained:

* **2,112 images**
* **43 ingredient classes**
* YOLO-format annotations
* Bounding-box and segmentation annotations

The raw dataset is preserved under:

```text
raw/sequel_farmer/
```

The processed dataset is stored under:

```text
processed/indian_ingredients/
```

### Dataset Split

| Split      |    Images |
| ---------- | --------: |
| Training   |     1,666 |
| Validation |       297 |
| Testing    |       149 |
| **Total**  | **2,112** |

The original test set was preserved and used as the final held-out test set.

### License

The Roboflow dataset page lists the dataset under **CC BY 4.0**.

---

## 1.2 Indian Spices Image Dataset

The Indian spice classification task uses the **Indian Spices Image Dataset** from Mendeley Data.

**Dataset source:**

https://data.mendeley.com/datasets/vg77y9rtjb/3

The dataset is **Version 3**, published on **4 September 2024**, with DOI:

```text
10.17632/vg77y9rtjb.3
```

The dataset contains **10,991 images covering 19 distinct types of Indian spices**.

### Dataset Split

| Split      |     Images |
| ---------- | ---------: |
| Training   |      8,786 |
| Validation |      1,092 |
| Testing    |      1,113 |
| **Total**  | **10,991** |

The processed dataset is stored under:

```text
processed/indian_spices/
├── train/
├── val/
├── test/
└── manifest.csv
```

### License

The Mendeley dataset is provided under **CC BY 4.0**.

---

## 1.3 Allergen30 Dataset

The **Allergen30** dataset was used for object detection.

**Dataset source:**

https://data.mendeley.com/datasets/9ygs9vhnpw/1

The dataset is **Version 1**, published on **22 August 2022**, with DOI:

```text
10.17632/9ygs9vhnpw.1
```

The original dataset contains:

* **14,524 images**
* **30 object classes**
* YOLO-format object-detection annotations

The original dataset was downloaded and preserved without modifying the raw files.

The raw dataset is stored under:

```text
raw/allergen30/
```

The cleaned dataset is stored under:

```text
processed/allergen30/
```

### Original Dataset Split

| Split      |     Images |
| ---------- | ---------: |
| Training   |     12,684 |
| Validation |      1,206 |
| Testing    |        634 |
| **Total**  | **14,524** |

### Classes Removed

For the Jivanya project, classes that were not required for the target ingredient/food detection scope were removed.

The following 11 classes were excluded:

```text
almond
avocado
blackberry
blueberry
pasta
pineapple
pistachio
pizza
roti
strawberry
tomato
```

### Final Classes

The cleaned dataset contains **19 classes**:

```text
0  alcohol
1  alcohol_glass
2  bread
3  bread_loaf
4  capsicum
5  cheese
6  chocolate
7  cooked_meat
8  dates
9  egg
10 eggplant
11 icecream
12 milk
13 milk_based_beverage
14 mushroom
15 non_milk_based_beverage
16 raw_meat
17 spinach
18 whole_egg_boiled
```

### Cleaning Results

| Split      | Images Kept | Images Removed | Objects Kept | Objects Removed |
| ---------- | ----------: | -------------: | -----------: | --------------: |
| Training   |       8,423 |          4,261 |       23,480 |          13,570 |
| Validation |         796 |            410 |        2,281 |           1,324 |
| Testing    |         427 |            207 |        1,144 |             801 |
| **Total**  |   **9,646** |      **4,878** |   **26,905** |      **15,695** |

### Final Dataset Integrity

```text
Training:
8423 images
8423 labels

Validation:
796 images
796 labels

Testing:
427 images
427 labels
```

No invalid annotations were found after cleaning.

```text
Empty labels: 0
Invalid annotations: 0
```

### License

The Allergen30 dataset is provided under **CC BY 4.0**.

---

## 1.4 Grocery Detection Dataset

The **Grocery Detection** dataset was used for detecting packaged grocery ingredients.

**Dataset source:**

https://universe.roboflow.com/grocdetect/grocery_detection-insij

The downloaded dataset is **Version 1** and contains four original classes:

```text
atta
maida
suji
vermicelli
```

The raw dataset is preserved under:

```text
raw/grocery_detection/
```

The processed datasets are stored under:

```text
processed/grocery_detection/
processed/grocery_detection_3class/
```

### Original Dataset Split

| Split      |  Images |
| ---------- | ------: |
| Training   |     333 |
| Validation |      95 |
| Testing    |      47 |
| **Total**  | **475** |

All 475 images have corresponding label files.

### Original Class Distribution

| Class      |  Images | Objects |
| ---------- | ------: | ------: |
| Atta       |     158 |     171 |
| Maida      |     132 |     141 |
| Suji       |      26 |      27 |
| Vermicelli |     170 |     172 |
| **Total**  | **463** | **511** |

Some images contained multiple annotated objects, while 12 images had empty annotation files.

### Annotation Conversion

The original Grocery Detection annotations were polygon-based YOLO annotations rather than standard five-field bounding-box annotations.

For object-detection training, polygon annotations were converted into YOLO bounding boxes using the minimum and maximum x/y coordinates of each polygon.

The raw dataset was not modified.

The conversion script is:

```text
scripts/convert_grocery_polygons.py
```

### Four-Class Dataset Validation

```text
Training:
333 images
333 labels
8 empty labels
0 invalid annotations

Validation:
95 images
95 labels
1 empty label
0 invalid annotations

Testing:
47 images
47 labels
3 empty labels
0 invalid annotations
```

### Four-Class Model Result

A four-class YOLO11n model was trained for 10 epochs.

The test results were:

| Metric    |    Result |
| --------- | --------: |
| Precision | **76.9%** |
| Recall    | **39.6%** |
| mAP@50    | **43.7%** |
| mAP@50–95 | **26.9%** |

The `suji` class produced unreliable detection performance, including **0% recall** on the test set.

Therefore, `suji` was excluded from the final Grocery Detection model.

---

# 2. Tasks and Models

The four datasets were used for different computer-vision tasks.

| Dataset           | Task                                     | Model             | Final Classes |
| ----------------- | ---------------------------------------- | ----------------- | ------------: |
| Sequel Farmer     | Object Detection + Instance Segmentation | YOLO11n-seg       |            43 |
| Indian Spices     | Image Classification                     | MobileNetV3-Small |            19 |
| Allergen30        | Object Detection                         | YOLO11n           |            19 |
| Grocery Detection | Object Detection                         | YOLO11n           |             3 |

---

# 3. Indian Ingredients Dataset Preparation

## 3.1 Raw Dataset

The original Sequel Farmer dataset was preserved under:

```text
raw/sequel_farmer/
```

The raw data was not modified directly.

The preparation process created a separate processed dataset under:

```text
processed/indian_ingredients/
```

---

## 3.2 Dataset Preparation Script

The dataset preparation script is:

```text
scripts/prepare_sequel_farmer.py
```

This script prepares the dataset into the project's standard directory structure.

The resulting structure is:

```text
processed/indian_ingredients/
├── train/
│   ├── images/
│   └── labels/
├── valid/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/
```

---

# 4. Annotation Cleaning

The original Sequel Farmer dataset contained a mixture of:

* YOLO bounding-box annotations
* YOLO segmentation annotations

A bounding-box annotation uses:

```text
class x_center y_center width height
```

Segmentation annotations contain polygon coordinates.

For consistent segmentation training, the five-field bounding-box annotations were converted into rectangular polygon annotations.

The cleaning script is:

```text
scripts/clean_sequel_farmer_labels.py
```

## Cleaning Results

| Operation                                      |      Count |
| ---------------------------------------------- | ---------: |
| Bounding-box annotations converted to polygons |     21,628 |
| Existing segmentation annotations retained     |     38,488 |
| **Total annotation lines processed**           | **60,116** |

After cleaning:

```text
Remaining 5-field labels: 0
Invalid segmentation annotation lines: 0
```

Therefore, the processed dataset contains segmentation-compatible annotations.

---

# 5. Indian Ingredients Class Imbalance

A major issue identified during dataset analysis was severe class imbalance.

The `chickpea` class was heavily overrepresented.

Across the complete original dataset:

```text
Total objects:       60,116
Chickpea objects:    58,744
```

Therefore:

```text
Chickpea object percentage: 97.72%
```

This means that approximately 97.72% of all annotated objects belong to the chickpea class.

---

## Chickpea Distribution

There were:

```text
1,402 images containing chickpea
```

with:

```text
58,744 chickpea objects
```

The number of chickpea objects per image ranged from:

```text
Minimum: 1
Maximum: 183
Average: 41.9
```

This showed that the imbalance was caused not only by the number of chickpea images, but also by the large number of chickpea objects present in individual images.

---

# 6. Dataset Balancing Experiments

Several approaches were tested to reduce the effect of class imbalance.

## 6.1 Balanced Image Split

A stratified split was created using:

```text
scripts/create_balanced_sequel_split.py
```

The resulting dataset contained:

```text
Training:   1,478 images
Validation:   317 images
Testing:     317 images
```

All 43 classes were represented in the splits.

However, this approach did not improve the final test performance.

---

## 6.2 Object-Balanced Dataset

A second experiment reduced the number of chickpea objects in the training dataset.

The script used was:

```text
scripts/create_yolo_object_balanced_split.py
```

The resulting training dataset contained approximately:

```text
Total objects:      1,994
Chickpea objects:   1,005
```

This approach also did not outperform the original training approach.

---

## 6.3 Minority-Class Image Oversampling

The final balancing strategy used **minority-class image oversampling**.

The script used was:

```text
scripts/create_oversampled_sequel_split.py
```

The strategy:

* Kept all original training images.
* Repeated images containing minority classes.
* Used a maximum repetition factor of 6×.
* Did not modify the validation set.
* Did not modify the test set.

The final oversampled training dataset contained:

```text
4,139 training entries
```

Validation and testing remained unchanged:

```text
Validation: 297 images
Test:       149 images
```

This approach produced the best test performance.

---

# 7. Indian Ingredient Model

## YOLO11n-seg

The final Indian ingredient model uses:

```text
YOLO11n-seg
```

The model supports both:

* Object detection
* Instance segmentation

The model was initialized using pretrained YOLO11n-seg weights.

---

## Training Configuration

| Parameter        | Value                 |
| ---------------- | --------------------- |
| Model            | YOLO11n-seg           |
| Task             | Instance Segmentation |
| Classes          | 43                    |
| Epochs           | 5                     |
| Image Size       | 320 × 320             |
| Batch Size       | 4                     |
| Workers          | 0                     |
| Device           | CPU                   |
| Training Dataset | Oversampled dataset   |

### Training Command

```bash
yolo segment train \
data=processed/indian_ingredients_oversampled/data.yaml \
model=yolo11n-seg.pt \
epochs=5 \
imgsz=320 \
batch=4 \
workers=0 \
device=cpu \
name=oversampled_sequel_farmer_5ep
```

---

# 8. Indian Ingredient Model Evaluation

The final model was evaluated on the original held-out test set:

```text
processed/indian_ingredients/test/
```

The test set contains:

```text
149 images
```

with approximately:

```text
5,564 annotated objects
```

During evaluation, 5 duplicate labels were removed by Ultralytics, resulting in 5,559 evaluated objects.

## Final Test Results

| Metric         |    Result |
| -------------- | --------: |
| Box Precision  | **0.262** |
| Box Recall     | **0.591** |
| Box mAP@50     | **0.407** |
| Box mAP@50–95  | **0.307** |
| Mask Precision | **0.220** |
| Mask Recall    | **0.543** |
| Mask mAP@50    | **0.353** |
| Mask mAP@50–95 | **0.202** |

---

# 9. Model Comparison

The different training approaches were compared using the same original held-out test set.

| Training Strategy               | Box mAP@50 | Mask mAP@50 |
| ------------------------------- | ---------: | ----------: |
| Original training               |      0.278 |       0.242 |
| Balanced split                  |      0.143 |       0.132 |
| Object-balanced training        |      0.129 |       0.120 |
| **Minority-class oversampling** |  **0.407** |   **0.353** |

The oversampling strategy produced the best overall performance.

Compared with the original model:

```text
Box mAP@50:
0.278 → 0.407

Mask mAP@50:
0.242 → 0.353

Box Recall:
0.318 → 0.591

Mask Recall:
0.246 → 0.543
```

Therefore, the oversampled YOLO11n-seg model was selected as the final ingredient model.

---

# 10. Final Indian Ingredient Model

The final model is stored at:

```text
models/final/indian_ingredients_yolo11n_seg.pt
```

It was selected from:

```text
runs/segment/oversampled_sequel_farmer_5ep/weights/best.pt
```

Model size:

```text
Approximately 5.7 MB
```

---

# 11. Indian Ingredient Inference

The final model can be used with Ultralytics YOLO.

Example:

```bash
yolo segment predict \
model=models/final/indian_ingredients_yolo11n_seg.pt \
source=path/to/image.jpg \
imgsz=320 \
conf=0.25 \
device=cpu \
save=True
```

The model produces ingredient detections and segmentation masks.

A prediction utility is also available at:

```text
scripts/predict.py
```

---

# 12. Indian Spices Dataset

The second dataset used in this module is the **Indian Spices Image Dataset**.

Source:

```text
https://data.mendeley.com/datasets/vg77y9rtjb/3
```

According to the dataset page, it contains:

```text
10,991 images
19 Indian spice types
```

The dataset is intended for applications including machine learning and image recognition.

---

# 13. Indian Spice Classes

The 19 spice classes used in this project are:

1. Asafoetida
2. Bay Leaf
3. Black Cardamom
4. Black Pepper
5. Caraway seeds
6. Cinnamom stick
7. Cloves
8. Coriander Seeds
9. Cubeb Pepper
10. Cumin seeds
11. Dry Ginger
12. Dry red Chilly
13. Fennel seeds
14. Green Cardamom
15. Mace
16. Nutmeg
17. Poppy Seeds
18. Star Anise
19. Stone Flowers

---

# 14. Indian Spice Classification Model

The Indian Spice dataset was used to train an image-classification model using:

```text
MobileNetV3-Small
```

The model was trained from scratch.

## Training Configuration

| Parameter            | Value             |
| -------------------- | ----------------- |
| Model                | MobileNetV3-Small |
| Classes              | 19                |
| Image Size           | 160 × 160         |
| Batch Size           | 8                 |
| Epochs               | 10                |
| Learning Rate        | 0.001             |
| Workers              | 0                 |
| Device               | CPU               |
| Model Initialization | From scratch      |

Training images used augmentation including:

* Horizontal flipping
* Small-angle rotation
* Image resizing
* Tensor conversion
* ImageNet normalization

Validation images used resizing, tensor conversion, and normalization.

---

# 15. Indian Spice Classification Results

The trained MobileNetV3-Small classifier achieved:

```text
Best Validation Accuracy: 98.44%
Test Accuracy:            97.48%
```

The test set contained:

```text
1,113 images
```

Correct predictions:

```text
1,085
```

Incorrect predictions:

```text
28
```

## Overall Test Performance

| Metric                |     Result |
| --------------------- | ---------: |
| Test Accuracy         | **97.48%** |
| Correct Predictions   |  **1,085** |
| Incorrect Predictions |     **28** |
| Test Images           |  **1,113** |
| Macro Precision       | **0.9733** |
| Macro Recall          | **0.9671** |
| Macro F1-score        | **0.9691** |

---

# 16. Spice Classification Performance

Several classes achieved 100% test accuracy.

Examples include:

* Asafoetida
* Bay Leaf
* Black Pepper
* Caraway seeds
* Cloves
* Coriander Seeds
* Cubeb Pepper
* Cumin seeds
* Dry Ginger
* Dry red Chilly
* Green Cardamom
* Poppy Seeds

Some classes were more difficult:

| Class          | Test Accuracy |
| -------------- | ------------: |
| Black Cardamom |        91.43% |
| Cinnamom stick |        90.74% |
| Fennel seeds   |        93.18% |
| Mace           |        97.67% |
| Nutmeg         |        70.59% |
| Star Anise     |        98.36% |
| Stone Flowers  |        95.51% |

Nutmeg was the most difficult class in the test set.

---

# 17. Spice Classification Errors

The 28 incorrect predictions included the following confusions:

```text
Black Cardamom → Cloves
Cinnamom stick → Mace
Cinnamom stick → Star Anise
Fennel seeds → Caraway seeds
Fennel seeds → Nutmeg
Mace → Dry red Chilly
Nutmeg → Black Cardamom
Nutmeg → Cloves
Star Anise → Dry red Chilly
Stone Flowers → Cubeb Pepper
Stone Flowers → Fennel seeds
```

These errors show that visually similar spices can be more difficult for the classifier to distinguish.

---

# 18. Spice Classifier Inference

The reusable spice classifier is:

```text
scripts/indian_spice_classifier.py
```

Example:

```python
from scripts.indian_spice_classifier import IndianSpiceClassifier

classifier = IndianSpiceClassifier()

result = classifier.predict(
    "path/to/spice_image.jpg"
)

print(result)
```

Example output:

```text
{
    'predicted_spice': 'Nutmeg',
    'confidence': 97.4
}
```

---

# 19. Spice Evaluation Results

Detailed evaluation results are stored in:

```text
models/evaluation_results.json
```

The file contains the classification evaluation results generated during testing.

---

# 20. External Spice Image Testing

An additional qualitative test was performed using an external Nutmeg image that was not part of the original test dataset.

The classifier predicted:

```text
Predicted Spice : Dry red Chilly
Confidence      : 53.81%
```

Top predictions:

```text
1. Dry red Chilly   53.81%
2. Cinnamom stick   34.20%
3. Mace              8.06%
4. Green Cardamom    1.85%
5. Asafoetida        1.46%
```

This demonstrates **domain shift** between the original dataset and external images.

Therefore, the reported 97.48% test accuracy represents performance on the prepared held-out test dataset and should not be interpreted as a guarantee of the same performance on every real-world image.

---

# 21. Allergen30 Dataset Preparation

The original Allergen30 dataset was preserved under:

```text
raw/allergen30/
```

The raw dataset was not modified.

The cleaned dataset was generated under:

```text
processed/allergen30/
```

The cleaning script is:

```text
scripts/clean_allergen30.py
```

The script:

* Reads the original YOLO dataset.
* Keeps the 19 required classes.
* Removes unwanted classes.
* Remaps class IDs.
* Copies only images containing retained annotations.
* Writes a new YOLO-compatible `data.yaml`.
* Preserves the original raw dataset.

The final processed structure is:

```text
processed/allergen30/
├── train/
│   ├── images/
│   └── labels/
├── valid/
│   ├── images/
│   └── labels/
├── test/
│   ├── images/
│   └── labels/
└── data.yaml
```

---

# 22. Allergen30 Model

The Allergen30 dataset was used for **object detection** using:

```text
YOLO11n
```

Unlike the Sequel Farmer model, this model uses bounding-box detection rather than instance segmentation.

## Training Configuration

| Parameter  | Value            |
| ---------- | ---------------- |
| Model      | YOLO11n          |
| Task       | Object Detection |
| Classes    | 19               |
| Epochs     | 10               |
| Image Size | 320 × 320        |
| Batch Size | 4                |
| Workers    | 0                |
| Device     | CPU              |

The model was trained initially for 5 epochs and then continued to 10 epochs.

The best checkpoint was selected based on validation performance.

---

# 23. Allergen30 Model Evaluation

The final Allergen30 model was evaluated on the cleaned held-out test set.

```text
Test images: 427
Test objects: 1,144
```

## Final Test Results

| Metric    |     Result |
| --------- | ---------: |
| Precision | **78.46%** |
| Recall    | **64.50%** |
| mAP@50    | **72.50%** |
| mAP@50–95 | **48.95%** |

These results show substantially stronger object-detection performance than the Grocery Detection dataset.

### Per-Class mAP@50–95

| Class                   | mAP@50–95 |
| ----------------------- | --------: |
| alcohol                 |     0.515 |
| alcohol_glass           |     0.538 |
| bread                   |     0.325 |
| bread_loaf              |     0.522 |
| capsicum                |     0.495 |
| cheese                  |     0.588 |
| chocolate               |     0.366 |
| cooked_meat             |     0.339 |
| dates                   |     0.150 |
| egg                     |     0.619 |
| eggplant                |     0.398 |
| icecream                |     0.347 |
| milk                    |     0.569 |
| milk_based_beverage     |     0.640 |
| mushroom                |     0.331 |
| non_milk_based_beverage |     0.623 |
| raw_meat                |     0.556 |
| spinach                 |     0.803 |
| whole_egg_boiled        |     0.577 |

The `spinach` class achieved the highest mAP@50–95, while `dates` was the most difficult class.

---

# 24. Final Allergen30 Model

The final Allergen30 model is stored at:

```text
models/final/allergen30_yolo11n.pt
```

It was selected from:

```text
runs/detect/runs/detect/allergen30_10ep_continued/weights/best.pt
```

The model is a YOLO11n object-detection model trained on the cleaned 19-class Allergen30 dataset.

---

# 25. Grocery Detection Dataset Preparation

The original Grocery Detection dataset was preserved under:

```text
raw/grocery_detection/
```

The raw data was not modified.

The original four-class processed dataset is stored under:

```text
processed/grocery_detection/
```

A second processed dataset was created after removing the unreliable `suji` class:

```text
processed/grocery_detection_3class/
```

The preparation script is:

```text
scripts/prepare_grocery_3class.py
```

The annotation conversion script is:

```text
scripts/convert_grocery_polygons.py
```

The final three classes are:

```text
0 atta
1 maida
2 vermicelli
```

---

# 26. Grocery Detection 3-Class Dataset

The final Grocery Detection dataset contains:

| Split      |  Images |  Labels |
| ---------- | ------: | ------: |
| Training   |     308 |     308 |
| Validation |      87 |      87 |
| Testing    |      42 |      42 |
| **Total**  | **437** | **437** |

Integrity validation showed:

```text
Training:
308 images
308 labels
0 empty
0 invalid

Validation:
87 images
87 labels
0 empty
0 invalid

Testing:
42 images
42 labels
0 empty
0 invalid
```

The final three-class dataset is therefore valid for YOLO object-detection training.

---

# 27. Grocery Detection Model

The final Grocery Detection model uses:

```text
YOLO11n
```

The model detects:

```text
atta
maida
vermicelli
```

The model was trained for 10 epochs.

## Training Configuration

| Parameter  | Value            |
| ---------- | ---------------- |
| Model      | YOLO11n          |
| Task       | Object Detection |
| Classes    | 3                |
| Epochs     | 10               |
| Image Size | 320 × 320        |
| Batch Size | 4                |
| Workers    | 0                |
| Device     | CPU              |

---

# 28. Grocery Detection Model Evaluation

The final three-class model was evaluated on the held-out test set.

```text
Test images: 42
Test objects: 46
```

## Final Test Results

| Metric    |    Result |
| --------- | --------: |
| Precision | **59.0%** |
| Recall    | **58.6%** |
| mAP@50    | **49.1%** |
| mAP@50–95 | **30.4%** |

### Per-Class Results

| Class      | Precision | Recall | mAP@50 | mAP@50–95 |
| ---------- | --------: | -----: | -----: | --------: |
| Atta       |     65.0% |  42.2% |  50.4% |     30.2% |
| Maida      |     30.0% |  57.1% |  27.9% |     19.9% |
| Vermicelli |     81.9% |  76.5% |  69.0% |     40.9% |

Vermicelli was the strongest-performing class.

Maida was the weakest class, although its test set contained only 7 images and 7 objects, so its per-class test metrics should be interpreted cautiously.

---

# 29. Grocery Model Comparison

The original four-class model was compared with the final three-class model.

| Metric    | 4-Class Model | 3-Class Model |
| --------- | ------------: | ------------: |
| Precision |     **76.9%** |         59.0% |
| Recall    |         39.6% |     **58.6%** |
| mAP@50    |         43.7% |     **49.1%** |
| mAP@50–95 |         26.9% |     **30.4%** |

Although precision decreased after removing `suji`, the final three-class model achieved better:

* Recall
* mAP@50
* mAP@50–95

The `suji` class was therefore excluded from the final model because its detection was unreliable.

---

# 30. Grocery Real-World Image Testing

Additional tests were performed using external images that were not part of the Grocery Detection dataset.

### Atta Image

An external image of atta was tested using:

```text
/home/mousumi/Pictures/Atta_flour.jpg
```

The model detected:

```text
atta
maida
```

At a low confidence threshold, the atta object was detected correctly, but a false-positive maida detection was also produced.

At a lower inference threshold, the approximate confidences included:

```text
maida: 63.69%
atta:  53.46%
```

### Wheat Flour Image

Another external image:

```text
/home/mousumi/Pictures/wheat-flour-chakki-atta-1000x1000.webp
```

The model detected:

```text
atta
vermicelli
```

The atta prediction was correct, while the vermicelli detection was a false positive.

### Additional Test

An external image:

```text
/home/mousumi/Pictures/images.jpeg
```

produced:

```text
maida
```

These tests show that the Grocery Detection model can perform inference on external images but may produce false positives when image appearance differs from the training data.

---

# 31. Final Grocery Detection Model

The final model is stored at:

```text
models/final/grocery_detection_yolo11n.pt
```

It was selected from:

```text
runs/detect/runs/detect/grocery_detection_3class_10ep/weights/best.pt
```

Final classes:

```text
atta
maida
vermicelli
```

---

# 32. Project Directory Structure

```text
indian_ingredients/
│
├── raw/
│   ├── sequel_farmer/
│   ├── indian_spices/
│   ├── allergen30/
│   └── grocery_detection/
│
├── processed/
│   ├── indian_ingredients/
│   ├── indian_ingredients_backup/
│   ├── indian_ingredients_balanced/
│   ├── indian_ingredients_yolo_balanced/
│   ├── indian_ingredients_oversampled/
│   ├── indian_spices/
│   ├── allergen30/
│   ├── grocery_detection/
│   └── grocery_detection_3class/
│
├── scripts/
│   ├── prepare_sequel_farmer.py
│   ├── clean_sequel_farmer_labels.py
│   ├── create_balanced_sequel_split.py
│   ├── create_yolo_object_balanced_split.py
│   ├── create_oversampled_sequel_split.py
│   ├── clean_allergen30.py
│   ├── convert_grocery_polygons.py
│   ├── prepare_grocery_3class.py
│   ├── predict.py
│   └── indian_spice_classifier.py
│
├── models/
│   ├── final/
│   │   ├── indian_ingredients_yolo11n_seg.pt
│   │   ├── allergen30_yolo11n.pt
│   │   └── grocery_detection_yolo11n.pt
│   │
│   ├── indian_spices_mobilenetv3.pth
│   ├── indian_spices_classes.json
│   └── evaluation_results.json
│
├── metadata/
│   ├── classes.csv
│   └── image_manifest.csv
│
├── runs/
│
├── MODEL_RESULTS.md
│
└── README.md
```

---

# 33. Main Scripts

| Script                                 | Purpose                                               |
| -------------------------------------- | ----------------------------------------------------- |
| `prepare_sequel_farmer.py`             | Prepare the Sequel Farmer dataset                     |
| `clean_sequel_farmer_labels.py`        | Clean and convert YOLO annotations                    |
| `create_balanced_sequel_split.py`      | Create a stratified dataset split                     |
| `create_yolo_object_balanced_split.py` | Create object-balanced training data                  |
| `create_oversampled_sequel_split.py`   | Oversample minority-class images                      |
| `clean_allergen30.py`                  | Clean and remap Allergen30 classes                    |
| `convert_grocery_polygons.py`          | Convert Grocery polygon annotations to bounding boxes |
| `prepare_grocery_3class.py`            | Prepare the final three-class Grocery dataset         |
| `predict.py`                           | Ingredient segmentation inference                     |
| `indian_spice_classifier.py`           | Indian spice classification inference                 |

---

# 34. Technologies Used

The machine-learning component uses:

* Python
* PyTorch
* Torchvision
* Ultralytics YOLO
* YOLO11n
* YOLO11n-seg
* MobileNetV3-Small
* Pillow
* NumPy
* Scikit-learn
* Ubuntu/Linux
* CPU-based training and inference

---

# 35. Limitations

## Indian Ingredient Segmentation

The Sequel Farmer dataset has severe class imbalance, especially for chickpea.

Several minority classes contain very few images and objects. Therefore, individual per-class metrics for rare classes can be unstable.

The oversampling strategy improved the overall model performance, but oversampling does not create genuinely new visual information.

More diverse real images for minority classes would likely improve generalization.

## Indian Spice Classification

The spice classifier achieved 97.48% test accuracy on the held-out dataset.

However, visually similar spices can still be confused.

External-image testing also demonstrated domain shift.

Differences in:

* Lighting
* Background
* Image quality
* Camera conditions
* Object arrangement
* Image style

can affect predictions.

## Allergen30 Object Detection

The Allergen30 model achieved strong overall test performance, but individual classes vary considerably.

Classes with fewer examples or visually difficult appearances may have lower detection performance.

For example:

```text
dates mAP@50–95: 0.150
```

Therefore, the overall mAP should not be interpreted as equal performance across every class.

## Grocery Detection

The Grocery Detection dataset is comparatively small.

The final test set contains only:

```text
42 images
46 objects
```

Therefore, test metrics can be sensitive to individual predictions.

The model also showed false positives during external-image testing.

The removal of `suji` improved recall and mAP, but the remaining classes still require more diverse real-world training data for stronger generalization.

---

# 36. Contribution

This module represents the **dataset and machine-learning contribution** to the Jivanya project.

The work includes:

1. Dataset collection and organization
2. Dataset preparation
3. Annotation cleaning
4. Segmentation-label conversion
5. Bounding-box conversion
6. Dataset integrity checking
7. Class-distribution analysis
8. Class-imbalance analysis
9. Dataset balancing experiments
10. Minority-class oversampling
11. YOLO11n-seg training
12. Ingredient segmentation testing
13. Indian spice dataset preparation
14. MobileNetV3-Small classification training
15. Spice classification evaluation
16. Allergen30 class filtering and remapping
17. Allergen30 YOLO11n training
18. Grocery Detection annotation conversion
19. Grocery class-selection experiments
20. Grocery YOLO11n training
21. Error analysis
22. External image testing
23. Final model selection
24. Inference script preparation

---

# 37. Final Models

## Indian Ingredient Segmentation

```text
models/final/indian_ingredients_yolo11n_seg.pt
```

Model:

```text
YOLO11n-seg
```

Final test performance:

```text
Box Precision:   0.262
Box Recall:      0.591
Box mAP@50:      0.407
Box mAP@50–95:   0.307

Mask Precision:  0.220
Mask Recall:     0.543
Mask mAP@50:     0.353
Mask mAP@50–95:  0.202
```

## Indian Spice Classification

Model:

```text
MobileNetV3-Small
```

Final test performance:

```text
Accuracy: 97.48%
Correct:  1,085 / 1,113
```

Model file:

```text
models/indian_spices_mobilenetv3.pth
```

## Allergen30 Object Detection

Model:

```text
YOLO11n
```

Final model:

```text
models/final/allergen30_yolo11n.pt
```

Final test performance:

```text
Precision:   78.46%
Recall:      64.50%
mAP@50:      72.50%
mAP@50–95:   48.95%
```

## Grocery Detection

Model:

```text
YOLO11n
```

Final classes:

```text
atta
maida
vermicelli
```

Final model:

```text
models/final/grocery_detection_yolo11n.pt
```

Final test performance:

```text
Precision:   59.0%
Recall:      58.6%
mAP@50:      49.1%
mAP@50–95:   30.4%
```

---

# 38. Dataset Sources

### Sequel Farmer Dataset

Roboflow Universe:

https://universe.roboflow.com/ayushi-beutb/sequel-farmer-cxwdj

Dataset version used in this project:

```text
Version 1
2,112 images
43 classes
```

License:

```text
CC BY 4.0
```

### Indian Spices Image Dataset

Mendeley Data:

https://data.mendeley.com/datasets/vg77y9rtjb/3

Dataset version:

```text
Version 3
10,991 images
19 spice types
```

DOI:

```text
10.17632/vg77y9rtjb.3
```

License:

```text
CC BY 4.0
```

### Allergen30 Dataset

Mendeley Data:

https://data.mendeley.com/datasets/9ygs9vhnpw/1

Dataset version:

```text
Version 1
14,524 original images
30 original classes
19 final classes
```

DOI:

```text
10.17632/9ygs9vhnpw.1
```

License:

```text
CC BY 4.0
```

### Grocery Detection Dataset

Roboflow Universe:

https://universe.roboflow.com/grocdetect/grocery_detection-insij

Dataset version:

```text
Version 1
475 original images
4 original classes
3 final classes
```

License:

```text
CC BY 4.0
```

---

# 39. Final Status

```text
INDIAN INGREDIENTS
────────────────────────────────────
Dataset Collection             ✓ Completed
Dataset Preparation            ✓ Completed
Annotation Cleaning            ✓ Completed
Annotation Validation          ✓ Completed
Class Imbalance Analysis       ✓ Completed
Balancing Experiments          ✓ Completed
YOLO11n-seg Training           ✓ Completed
Model Testing                  ✓ Completed
Final Model Selection          ✓ Completed
Inference Script               ✓ Completed


INDIAN SPICES
────────────────────────────────────
Dataset Collection             ✓ Completed
Dataset Preparation            ✓ Completed
19-Class Classification        ✓ Completed
MobileNetV3-Small Training     ✓ Completed
Model Evaluation               ✓ Completed
Error Analysis                 ✓ Completed
External Image Testing         ✓ Completed
Inference Script               ✓ Completed


ALLERGEN30
────────────────────────────────────
Dataset Collection             ✓ Completed
Class Filtering                ✓ Completed
Class Remapping                ✓ Completed
Dataset Validation             ✓ Completed
YOLO11n Training               ✓ Completed
Model Evaluation               ✓ Completed
Final Model Selection          ✓ Completed


GROCERY DETECTION
────────────────────────────────────
Dataset Collection             ✓ Completed
Annotation Conversion          ✓ Completed
4-Class Experiment             ✓ Completed
Suji Evaluation                ✓ Completed
3-Class Dataset Preparation    ✓ Completed
Dataset Validation             ✓ Completed
YOLO11n Training               ✓ Completed
Model Evaluation               ✓ Completed
External Image Testing         ✓ Completed
Final Model Selection          ✓ Completed
```

---

# 40. Final Deliverables

The main machine-learning deliverables are:

```text
models/final/indian_ingredients_yolo11n_seg.pt
models/indian_spices_mobilenetv3.pth
models/final/allergen30_yolo11n.pt
models/final/grocery_detection_yolo11n.pt

models/evaluation_results.json

scripts/predict.py
scripts/indian_spice_classifier.py
scripts/clean_allergen30.py
scripts/convert_grocery_polygons.py
scripts/prepare_grocery_3class.py
```
