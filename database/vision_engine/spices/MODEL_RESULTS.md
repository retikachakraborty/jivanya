# Indian Spices Classification — Model Results

## Model Summary

- Model: MobileNetV3-Small
- Task: Multi-class image classification
- Dataset: Indian Spices Image Dataset
- Classes: 19
- Test images: 1,113
- Correct predictions: 1,085
- Incorrect predictions: 28
- Test Accuracy: 97.48%
- Image size: 160 × 160
- Training epochs: 10
- Training device: CPU

## Overall Metrics

| Metric | Score |
|---|---:|
| Accuracy | 97.48% |
| Macro Precision | 97.33% |
| Macro Recall | 96.71% |
| Macro F1-score | 96.91% |
| Weighted Precision | 97.54% |
| Weighted Recall | 97.48% |
| Weighted F1-score | 97.43% |

## Best Performing Classes

The following classes achieved 100% precision, recall, and F1-score:

- Asafoetida
- Bay Leaf
- Black Pepper
- Coriander Seeds
- Cumin seeds
- Dry Ginger
- Green Cardamom
- Poppy Seeds

## Main Areas for Improvement

- Nutmeg: recall 70.59%, F1-score 80.00%. Mainly confused with Black Cardamom and Cloves.
- Black Cardamom: recall 91.43%, F1-score 88.89%. Three images were classified as Cloves.
- Cinnamom stick: recall 90.74%. Four images were classified as Mace and one as Star Anise.
- Fennel seeds: recall 93.18%. Errors involved Caraway seeds and Nutmeg.
- Stone Flowers: recall 95.51%. Errors involved Cubeb Pepper and Fennel seeds.

## Conclusion

The MobileNetV3-Small classifier achieved 97.48% test accuracy on 1,113 test images, correctly classifying 1,085 images and misclassifying 28 images.

The model achieved a 96.91% macro F1-score and 97.43% weighted F1-score, demonstrating strong classification performance across the 19 Indian spice classes.

The main remaining challenge is distinguishing visually similar spices, particularly Nutmeg, Black Cardamom, Cloves, Cinnamom stick, and related classes.

## Evaluation Artifact

Detailed machine-readable evaluation results are saved at:

`database/vision_engine/spices/models/evaluation_results.json`
