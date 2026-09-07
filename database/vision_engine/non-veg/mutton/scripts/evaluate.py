from ultralytics import YOLO

MODEL_PATH = "runs/detect/runs/detect/mutton_yolov8n-2/weights/best.pt"
DATA_PATH = "database/vision_engine/non-veg/mutton/data.yaml"

model = YOLO(MODEL_PATH)

model.val(
    data=DATA_PATH,
    split="test",
    imgsz=640,
)
