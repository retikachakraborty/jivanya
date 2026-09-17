from ultralytics import YOLO

DATA_PATH = "database/vision_engine/tea/Green_Tea/processed/Green_Tea/data.yaml"

model = YOLO("yolov8n.pt")

model.train(
    data=DATA_PATH,
    epochs=10,
    imgsz=640,
    batch=16,
    device="cpu",
    project="database/vision_engine/tea/Green_Tea/runs",
    name="green_tea_yolov8n",
    patience=5,
)
