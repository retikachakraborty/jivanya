from ultralytics import YOLO

DATASET = "database/vision_engine/non-veg/fish/processed/data.yaml"
MODEL = "yolo11n.pt"

def main():
    model = YOLO(MODEL)

    model.train(
        data=DATASET,
        epochs=50,
        imgsz=640,
        batch=8,
        project="database/vision_engine/non-veg/fish/models",
        name="fish_yolo11n",
    )

if __name__ == "__main__":
    main()
