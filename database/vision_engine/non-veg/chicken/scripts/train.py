from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(
    data="database/vision_engine/non-veg/chicken/processed/data.yaml",
    epochs=10,
    imgsz=640,
    batch=8,
    project="runs",
    name="chicken_yolov8n",
    patience=5
)
