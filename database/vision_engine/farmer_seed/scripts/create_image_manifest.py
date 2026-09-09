from pathlib import Path
import csv

BASE = Path("/home/mousumi/Documents/final project/jivanya/database/vision_engine/farmer_seed")
PROCESSED = BASE / "processed" / "indian_ingredients"
OUTPUT = BASE / "metadata" / "image_manifest.csv"

SPLITS = ["train", "valid", "test"]

def main():
    rows = []

    for split in SPLITS:
        image_dir = PROCESSED / split / "images"
        label_dir = PROCESSED / split / "labels"

        for image in sorted(image_dir.iterdir()):
            if image.is_file():
                label = label_dir / f"{image.stem}.txt"

                rows.append({
                    "image_name": image.name,
                    "split": split,
                    "source": "sequel_farmer",
                    "label_file": label.name if label.exists() else ""
                })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["image_name", "split", "source", "label_file"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created: {OUTPUT}")
    print(f"Total images: {len(rows)}")

    for split in SPLITS:
        count = sum(1 for row in rows if row["split"] == split)
        print(f"{split}: {count}")

if __name__ == "__main__":
    main()
