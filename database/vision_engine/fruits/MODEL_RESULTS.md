# Fruit Detection Model Results

## Model

- Architecture: YOLO11n
- Task: Object Detection
- Image size: 640
- Classes: 6
- Dataset images: 8,479

## Classes

1. Apple
2. Banana
3. Grape
4. Orange
5. Pineapple
6. Watermelon

## Dataset Distribution

| Class | Images | Bounding Boxes |
|---|---:|---:|
| Apple | 1,865 | 7,049 |
| Banana | 1,460 | 3,536 |
| Grape | 1,746 | 7,202 |
| Orange | 2,107 | 15,549 |
| Pineapple | 718 | 1,613 |
| Watermelon | 900 | 1,976 |

Total bounding boxes: 36,925.

## Training

Initial baseline training was performed for 3 epochs.

The resulting checkpoint was then used for an additional
7-epoch training stage.

## Final Validation Metrics

- Precision: 0.614
- Recall: 0.435
- mAP@50: 0.477
- mAP@50-95: 0.313

## Real-World Testing

The final model was tested using external fruit images not taken
from the training dataset.

The model successfully detected the supported fruit classes in
the final real-world tests, including mixed-fruit scenes.

External test screenshots are intentionally excluded from Git
because they were collected from web sources and are used only
for local model validation.

## Final Model

models/final/fruits_yolo11n.pt
