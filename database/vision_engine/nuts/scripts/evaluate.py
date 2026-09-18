from ultralytics import YOLO

MODEL_PATH = "runs/classify/database/vision_engine/nuts/runs/nuts_yolov8n/weights/best.pt"
DATA_PATH = "database/vision_engine/nuts/processed"

model = YOLO(MODEL_PATH)

model.val(
    data=DATA_PATH,
    split="test",
    imgsz=224,
    device="cpu",
)
