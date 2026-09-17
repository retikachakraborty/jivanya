from ultralytics import YOLO

MODEL_PATH = "database/vision_engine/tea/Green_Tea/runs/green_tea_yolov8n/weights/best.pt"
DATA_PATH = "database/vision_engine/tea/Green_Tea/processed/Green_Tea/data.yaml"

model = YOLO(MODEL_PATH)

model.val(
    data=DATA_PATH,
    split="test",
    imgsz=640,
    device="cpu",
)
