from pathlib import Path
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[4]

MODEL = (
    ROOT
    / "database/vision_engine/fruits/models/final/fruits_yolo11n.pt"
)

DATA = (
    ROOT
    / "database/vision_engine/fruits/processed/data.yaml"
)

model = YOLO(MODEL)

metrics = model.val(
    data=str(DATA),
    split="test",
    imgsz=640,
)

print("\nFinal test metrics")
print("------------------")
print("Precision:", metrics.box.mp)
print("Recall:", metrics.box.mr)
print("mAP50:", metrics.box.map50)
print("mAP50-95:", metrics.box.map)
