from pathlib import Path
import shutil

RAW_ROOT = Path("raw/allergen30/Allergen30")
OUT_ROOT = Path("processed/allergen30")

CLASS_NAMES = [
    "alcohol",
    "alcohol_glass",
    "almond",
    "avocado",
    "blackberry",
    "blueberry",
    "bread",
    "bread_loaf",
    "capsicum",
    "cheese",
    "chocolate",
    "cooked_meat",
    "dates",
    "egg",
    "eggplant",
    "icecream",
    "milk",
    "milk_based_beverage",
    "mushroom",
    "non_milk_based_beverage",
    "pasta",
    "pineapple",
    "pistachio",
    "pizza",
    "raw_meat",
    "roti",
    "spinach",
    "strawberry",
    "tomato",
    "whole_egg_boiled",
]

KEEP_CLASSES = [
    "alcohol",
    "alcohol_glass",
    "bread",
    "bread_loaf",
    "capsicum",
    "cheese",
    "chocolate",
    "cooked_meat",
    "dates",
    "egg",
    "eggplant",
    "icecream",
    "milk",
    "milk_based_beverage",
    "mushroom",
    "non_milk_based_beverage",
    "raw_meat",
    "spinach",
    "whole_egg_boiled",
]

KEEP_IDS = {CLASS_NAMES.index(name): new_id
            for new_id, name in enumerate(KEEP_CLASSES)}

def process_split(split):
    src_images = RAW_ROOT / split / "images"
    src_labels = RAW_ROOT / split / "labels"

    dst_images = OUT_ROOT / split / "images"
    dst_labels = OUT_ROOT / split / "labels"

    dst_images.mkdir(parents=True, exist_ok=True)
    dst_labels.mkdir(parents=True, exist_ok=True)

    kept_images = 0
    removed_images = 0
    kept_objects = 0
    removed_objects = 0

    for label_file in sorted(src_labels.glob("*.txt")):
        image_file = src_images / f"{label_file.stem}.jpg"

        if not image_file.exists():
            # Try common image extensions
            for ext in [".jpeg", ".png", ".JPG", ".JPEG", ".PNG"]:
                candidate = src_images / f"{label_file.stem}{ext}"
                if candidate.exists():
                    image_file = candidate
                    break

        if not image_file.exists():
            print(f"WARNING: image missing for {label_file.name}")
            continue

        new_lines = []

        for line in label_file.read_text().splitlines():
            parts = line.strip().split()

            if len(parts) != 5:
                print(f"WARNING: invalid label line in {label_file}")
                continue

            old_id = int(parts[0])

            if old_id in KEEP_IDS:
                new_id = KEEP_IDS[old_id]
                new_lines.append(" ".join([str(new_id)] + parts[1:]))
                kept_objects += 1
            else:
                removed_objects += 1

        if new_lines:
            shutil.copy2(image_file, dst_images / image_file.name)

            (dst_labels / label_file.name).write_text(
                "\n".join(new_lines) + "\n"
            )

            kept_images += 1
        else:
            removed_images += 1

    return kept_images, removed_images, kept_objects, removed_objects


def write_yaml():
    yaml_text = """train: ../train/images
val: ../valid/images
test: ../test/images

nc: 19
names:
"""

    for i, name in enumerate(KEEP_CLASSES):
        yaml_text += f"  {i}: {name}\n"

    (OUT_ROOT / "data.yaml").write_text(yaml_text)


def main():
    print("Cleaning Allergen30...")
    print(f"Input : {RAW_ROOT}")
    print(f"Output: {OUT_ROOT}")
    print()

    total_kept_images = 0
    total_removed_images = 0
    total_kept_objects = 0
    total_removed_objects = 0

    for split in ["train", "valid", "test"]:
        result = process_split(split)

        kept_images, removed_images, kept_objects, removed_objects = result

        print(f"{split}:")
        print(f"  Images kept   : {kept_images}")
        print(f"  Images removed: {removed_images}")
        print(f"  Objects kept  : {kept_objects}")
        print(f"  Objects removed: {removed_objects}")
        print()

        total_kept_images += kept_images
        total_removed_images += removed_images
        total_kept_objects += kept_objects
        total_removed_objects += removed_objects

    write_yaml()

    print("===================================")
    print("Allergen30 cleaning completed.")
    print(f"Total images kept    : {total_kept_images}")
    print(f"Total images removed : {total_removed_images}")
    print(f"Total objects kept   : {total_kept_objects}")
    print(f"Total objects removed: {total_removed_objects}")
    print("Classes kept         : 19")
    print("===================================")


if __name__ == "__main__":
    main()
