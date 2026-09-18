from ultralytics import YOLO
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("source", help="Image, directory, or video to run detection on")
parser.add_argument("--conf", type=float, default=0.25)
args = parser.parse_args()

MODEL_PATH = "runs/detect/database/vision_engine/non-veg/chicken/runs/yolov8n_baseline-2/weights/best.pt"

model = YOLO(MODEL_PATH)

model.predict(
    source=args.source,
    conf=args.conf,
    save=True,
)
