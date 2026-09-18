# Chicken Dataset Processing

The original Roboflow dataset is stored locally under `raw/` and is not committed to Git.

The dataset contains polygon annotations and a small number of existing YOLO bounding-box annotations.

For YOLOv8 object detection training:

- Polygon annotations are converted to their enclosing bounding boxes.
- Existing 5-value YOLO bounding-box annotations are preserved.
- Processed images and labels are stored locally under `processed/`.
- The original `raw/` dataset remains unchanged.

The processing produced 2,800 training images, 80 validation images, and 40 test images.
