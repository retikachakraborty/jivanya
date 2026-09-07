from ultralytics import YOLO
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]

MODEL = ROOT / "models" / "final" / "vegetables_yolo11n.pt"

parser = argparse.ArgumentParser()
parser.add_argument(
    "--source",
    required=True,
    help="Image, directory, video, or camera source"
)
parser.add_argument("--conf", type=float, default=0.25)

args = parser.parse_args()

model = YOLO(str(MODEL))

model.predict(
    source=args.source,
    imgsz=640,
    conf=args.conf,
    save=True,
)
