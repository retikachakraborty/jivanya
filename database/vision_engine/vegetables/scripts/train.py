from ultralytics import YOLO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "processed" / "data.yaml"

model = YOLO("yolo11n.pt")

model.train(
    data=str(DATA),
    epochs=10,
    imgsz=640,
    batch=8,
    workers=2,
    project=str(ROOT / "runs" / "detect"),
    name="vegetables_yolo11n",
)
