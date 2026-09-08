# Allergen Vision Engine - Model Results

## Model Information

| Property | Value |
|---|---|
| Model | YOLO11n |
| Task | Object Detection |
| Parameters | 2,585,857 |
| GFLOPs | 6.4 |
| Framework | Ultralytics YOLO 8.4.143 |
| Image Size | 640 × 640 |
| Device | CPU |
| Test Images | 427 |
| Test Instances | 1,144 |
| Number of Classes | 19 |

## Overall Test Results

| Metric | Score |
|---|---:|
| Precision | 60.33% |
| Recall | 47.15% |
| mAP@50 | 51.64% |
| mAP@50-95 | 27.10% |
| Inference Time | 55.6 ms/image |

## Per-Class Results

| Class | Images | Instances | Precision | Recall | mAP@50 | mAP@50-95 |
|---|---:|---:|---:|---:|---:|---:|
| alcohol | 24 | 44 | 50.4% | 59.1% | 53.6% | 23.7% |
| alcohol_glass | 21 | 38 | 46.1% | 78.9% | 69.4% | 29.5% |
| bread | 45 | 107 | 50.0% | 33.6% | 37.1% | 17.2% |
| bread_loaf | 43 | 62 | 54.0% | 37.1% | 39.9% | 24.3% |
| capsicum | 13 | 39 | 87.0% | 68.8% | 77.9% | 44.8% |
| cheese | 29 | 55 | 68.8% | 50.9% | 57.6% | 34.7% |
| chocolate | 25 | 81 | 51.4% | 39.1% | 37.8% | 17.5% |
| cooked_meat | 16 | 27 | 23.1% | 37.0% | 31.4% | 13.2% |
| dates | 6 | 72 | 88.2% | 41.6% | 60.4% | 39.7% |
| egg | 68 | 100 | 63.7% | 57.0% | 64.4% | 38.5% |
| eggplant | 22 | 99 | 54.2% | 50.3% | 51.6% | 23.1% |
| icecream | 26 | 73 | 64.3% | 24.7% | 46.2% | 21.0% |
| milk | 28 | 52 | 63.1% | 52.5% | 63.7% | 33.8% |
| milk_based_beverage | 26 | 39 | 73.6% | 71.5% | 71.7% | 33.4% |
| mushroom | 5 | 71 | 85.6% | 9.86% | 25.5% | 16.3% |
| non_milk_based_beverage | 31 | 38 | 60.0% | 42.1% | 46.0% | 21.6% |
| raw_meat | 15 | 38 | 25.0% | 55.3% | 43.8% | 25.0% |
| spinach | 21 | 22 | 52.7% | 25.4% | 29.1% | 11.0% |
| whole_egg_boiled | 24 | 87 | 85.1% | 60.9% | 74.1% | 46.7% |

## Best Performing Classes

Based on mAP@50:

1. capsicum - 77.9%
2. whole_egg_boiled - 74.1%
3. milk_based_beverage - 71.7%
4. alcohol_glass - 69.4%
5. egg - 64.4%

These classes show comparatively strong detection performance on the test set.

## Classes Requiring Improvement

The classes with the lowest mAP@50 are:

1. mushroom - 25.5%
2. spinach - 29.1%
3. cooked_meat - 31.4%
4. chocolate - 37.8%
5. bread - 37.1%

The lower recall for mushroom (9.86%), spinach (25.4%), and icecream (24.7%) indicates that the model misses a substantial number of objects from these classes.

## Performance Interpretation

The model achieves an overall precision of 60.33%, meaning that a majority of its detected objects are correct. The recall of 47.15% indicates that the model still misses a considerable number of objects in the test dataset.

The mAP@50 score of 51.64% demonstrates moderate object-detection performance at the IoU 0.50 threshold. The stricter mAP@50-95 score of 27.10% shows that localization accuracy decreases when higher IoU thresholds are required.

The strongest results are observed for visually distinctive classes such as capsicum and whole_egg_boiled. Lower performance is observed for classes such as mushroom, spinach, cooked_meat, and chocolate, which may require additional training data, better representation, or improved object localization.

## Inference Performance

The evaluation was performed on CPU.

- Preprocessing: 2.1 ms/image
- Inference: 55.6 ms/image
- Postprocessing: 0.7 ms/image

The model is relatively lightweight with approximately 2.59 million parameters and 6.4 GFLOPs, making YOLO11n suitable for applications where a compact detection model is preferred.

## Evaluation Configuration

The evaluation used:

- Dataset: Allergen30 19-class test set
- Configuration: processed/allergen30_before_egg_removal/data.yaml
- Image size: 640
- Batch size: 8
- Device: CPU
- Validation split: test
- Ultralytics version: 8.4.143

Results were saved to:

runs/detect/val-3

## Important Dataset Note

The trained model uses the 19-class Allergen30 configuration containing egg and whole_egg_boiled. The current 19-class evaluation dataset matches the model class mapping and was therefore used for the reported results.

A separate processed/allergen30 configuration in the project contains 17 classes. That configuration does not match the class mapping of the trained 19-class model and should not be used to report the final performance of this model.

## Conclusion

The Allergen Vision Engine provides moderate overall object-detection performance with a precision of 60.33%, recall of 47.15%, mAP@50 of 51.64%, and mAP@50-95 of 27.10%.

The model performs particularly well on capsicum, whole_egg_boiled, milk_based_beverage, and alcohol_glass. Further training and dataset improvement would be beneficial for low-performing classes such as mushroom, spinach, cooked_meat, and chocolate.
