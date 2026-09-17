from ultralytics import YOLO
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("source", help="Image, directory, or video to run detection on")
parser.add_argument("--conf", type=float, default=0.25)
args = parser.parse_args()

MODEL_PATH = "database/vision_engine/tea/Red_Tea/runs/red_tea_yolov8n/weights/best.pt"

model = YOLO(MODEL_PATH)

model.predict(
    source=args.source,
    imgsz=640,
    device="cpu",
    conf=args.conf,
    save=True,
)
