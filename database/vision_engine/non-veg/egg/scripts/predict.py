from ultralytics import YOLO

MODEL = "database/vision_engine/non-veg/egg/models/final/egg_yolo11n.pt"

def main():
    model = YOLO(MODEL)

    model.predict(
        source="database/vision_engine/non-veg/egg/processed/test/images",
        imgsz=640,
        conf=0.25,
        save=True,
    )

if __name__ == "__main__":
    main()
