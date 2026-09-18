from ultralytics import YOLO

DATA_PATH = "database/vision_engine/coffee/processed"

model = YOLO("yolov8n-cls.pt")

model.train(
    data=DATA_PATH,
    epochs=10,
    imgsz=224,
    batch=16,
    device="cpu",
    project="database/vision_engine/coffee/runs",
    name="coffee_yolov8n",
)
