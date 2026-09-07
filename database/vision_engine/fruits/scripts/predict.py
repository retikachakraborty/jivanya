from pathlib import Path
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[4]

MODEL = (
    ROOT
    / "database/vision_engine/fruits/models/final/"
      "fruits_yolo11n.pt"
)

SOURCE = (
    ROOT
    / "database/vision_engine/fruits/test_images"
)

OUTPUT = (
    ROOT
    / "database/vision_engine/fruits/runs/detect"
)

model = YOLO(MODEL)

model.predict(
    source=str(SOURCE),
    imgsz=640,
    conf=0.25,
    save=True,
    save_txt=True,
    save_conf=True,
    project=str(OUTPUT),
    name="predictions",
)
