from pathlib import Path
import shutil

SOURCE = Path("../indian_ingredients_mousumi_backup/processed/allergen30")
DEST = Path("database/vision_engine/non-veg/egg/processed")

CLASS_MAP = {"9": "0", "18": "1"}

for split in ["train", "valid", "test"]:
    src_images = SOURCE / split / "images"
    src_labels = SOURCE / split / "labels"
    dst_images = DEST / split / "images"
    dst_labels = DEST / split / "labels"

    for label_file in src_labels.glob("*.txt"):
        kept = []

        for line in label_file.read_text().splitlines():
            parts = line.split()
            if len(parts) == 5 and parts[0] in CLASS_MAP:
                parts[0] = CLASS_MAP[parts[0]]
                kept.append(" ".join(parts))

        if kept:
            image_found = False
            for ext in [".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"]:
                image = src_images / (label_file.stem + ext)
                if image.exists():
                    shutil.copy2(image, dst_images / image.name)
                    image_found = True
                    break

            if image_found:
                (dst_labels / label_file.name).write_text("\n".join(kept) + "\n")

print("Egg dataset preparation complete.")
