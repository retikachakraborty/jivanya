from ultralytics import YOLO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MODEL = ROOT / "models" / "final" / "vegetables_yolo11n.pt"
DATA = ROOT / "processed" / "data.yaml"

model = YOLO(str(MODEL))

metrics = model.val(
    data=str(DATA),
    split="test",
    imgsz=640,
    batch=8,
)

print("Precision:", metrics.box.mp)
print("Recall:", metrics.box.mr)
print("mAP50:", metrics.box.map50)
print("mAP50-95:", metrics.box.map)
