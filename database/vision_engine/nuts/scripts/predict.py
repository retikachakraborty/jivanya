from ultralytics import YOLO
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("source", help="Image, directory, or other supported source")
parser.add_argument("--conf", type=float, default=0.25)
args = parser.parse_args()

MODEL_PATH = "runs/classify/database/vision_engine/nuts/runs/nuts_yolov8n/weights/best.pt"

model = YOLO(MODEL_PATH)

model.predict(
    source=args.source,
    imgsz=224,
    device="cpu",
    save=True,
)
