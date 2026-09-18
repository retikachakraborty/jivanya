from ultralytics import YOLO

MODEL_PATH = "runs/detect/database/vision_engine/non-veg/chicken/runs/yolov8n_baseline-2/weights/best.pt"
DATA_PATH = "database/vision_engine/non-veg/chicken/processed/data.yaml"

model = YOLO(MODEL_PATH)

model.val(
    data=DATA_PATH,
    split="test",
    imgsz=640,
)
