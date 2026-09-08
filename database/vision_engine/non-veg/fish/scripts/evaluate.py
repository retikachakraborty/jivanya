from ultralytics import YOLO

MODEL = "database/vision_engine/non-veg/fish/models/final/fish_yolo11n.pt"
DATASET = "database/vision_engine/non-veg/fish/processed/data.yaml"

def main():
    model = YOLO(MODEL)

    results = model.val(
        data=DATASET,
        split="test",
        imgsz=640,
        batch=8,
    )

    print(results.results_dict)

if __name__ == "__main__":
    main()
