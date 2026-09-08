from ultralytics import YOLO

MODEL = "database/vision_engine/non-veg/fish/models/final/fish_yolo11n.pt"

def main():
    model = YOLO(MODEL)

    model.predict(
        source="database/vision_engine/non-veg/fish/processed/test/images",
        imgsz=640,
        conf=0.25,
        save=True,
    )

if __name__ == "__main__":
    main()
