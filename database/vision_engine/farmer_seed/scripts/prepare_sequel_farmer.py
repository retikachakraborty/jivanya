from pathlib import Path
import shutil

BASE = Path("/home/mousumi/Documents/final project/jivanya/database/vision_engine/farmer_seed")

RAW = BASE / "raw" / "sequel_farmer"
PROCESSED = BASE / "processed" / "indian_ingredients"

SPLITS = ["train", "valid", "test"]


def copy_split(split):
    raw_images = RAW / split / "images"
    raw_labels = RAW / split / "labels"

    processed_images = PROCESSED / split / "images"
    processed_labels = PROCESSED / split / "labels"

    processed_images.mkdir(parents=True, exist_ok=True)
    processed_labels.mkdir(parents=True, exist_ok=True)

    image_count = 0
    label_count = 0

    for image in raw_images.iterdir():
        if image.is_file():
            shutil.copy2(image, processed_images / image.name)
            image_count += 1

    for label in raw_labels.iterdir():
        if label.is_file():
            shutil.copy2(label, processed_labels / label.name)
            label_count += 1

    print(f"{split}: {image_count} images, {label_count} labels")


def main():
    print("Preparing Sequel Farmer dataset...")
    print(f"RAW:       {RAW}")
    print(f"PROCESSED: {PROCESSED}")
    print()

    for split in SPLITS:
        copy_split(split)

    print()
    print("Dataset preparation completed successfully.")


if __name__ == "__main__":
    main()
