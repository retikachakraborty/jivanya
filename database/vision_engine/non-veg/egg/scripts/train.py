from ultralytics import YOLO

DATASET = "database/vision_engine/non-veg/egg/processed/data.yaml"
MODEL = "yolo11n.pt"

def main():
    model = YOLO(MODEL)

    model.train(
        data=DATASET,
        epochs=5,
        imgsz=640,
        batch=8,
        project="database/vision_engine/non-veg/egg/models",
        name="egg_yolo11n",
    )

if __name__ == "__main__":
    main()
