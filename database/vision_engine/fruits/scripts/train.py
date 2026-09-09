from pathlib import Path
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[4]

DATA = (
    ROOT
    / "database/vision_engine/fruits/processed/data.yaml"
)

RUNS = ROOT / "database/vision_engine/fruits/runs/detect"

model = YOLO(ROOT / "yolo11n.pt")

model.train(
    data=str(DATA),
    epochs=10,
    imgsz=640,
    batch=8,
    workers=2,
    device="cpu",
    project=str(RUNS),
    name="fruit_6class_training",
)
