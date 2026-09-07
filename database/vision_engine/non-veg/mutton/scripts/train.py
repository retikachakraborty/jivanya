from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(
    data="database/vision_engine/non-veg/mutton/data.yaml",
    epochs=10,
    imgsz=640,
    batch=16,
    project="runs",
    name="mutton_yolov8n",
    patience=5
)
