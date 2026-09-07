from pathlib import Path
import random
import shutil

BASE = Path("/home/mousumi/Documents/final project/jivanya/database/vision_engine/farmer_seed")

SOURCE = BASE / "processed" / "indian_ingredients_balanced"
OUTPUT = BASE / "processed" / "indian_ingredients_yolo_balanced"

SEED = 42
CHICKPEA_CLASS = 8
TARGET_CHICKPEA_OBJECTS = 1000

random.seed(SEED)


def read_labels(label_file):
    rows = []

    for line in label_file.read_text().splitlines():
        if not line.strip():
            continue

        parts = line.split()
        cls = int(float(parts[0]))
        rows.append((cls, line))

    return rows


def link_file(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)

    if dst.exists() or dst.is_symlink():
        dst.unlink()

    dst.symlink_to(src.resolve())


def prepare_train():
    source_images = SOURCE / "train" / "images"
    source_labels = SOURCE / "train" / "labels"

    output_images = OUTPUT / "train" / "images"
    output_labels = OUTPUT / "train" / "labels"

    output_images.mkdir(parents=True, exist_ok=True)
    output_labels.mkdir(parents=True, exist_ok=True)

    all_images = sorted(source_images.iterdir())

    minority_images = []
    pure_chickpea_images = []

    for image in all_images:
        label_file = source_labels / f"{image.stem}.txt"

        if not label_file.exists():
            continue

        rows = read_labels(label_file)

        classes = {cls for cls, _ in rows}
        chickpea_count = sum(
            1 for cls, _ in rows if cls == CHICKPEA_CLASS
        )

        # Keep every image containing a minority class.
        if any(cls != CHICKPEA_CLASS for cls in classes):
            minority_images.append((image, label_file, chickpea_count))
        elif chickpea_count > 0:
            pure_chickpea_images.append(
                (image, label_file, chickpea_count)
            )
        else:
            # Background/empty-label image.
            minority_images.append((image, label_file, 0))

    print(f"Total training images: {len(all_images)}")
    print(f"Images containing minority classes: {len(minority_images)}")
    print(f"Pure chickpea images available: {len(pure_chickpea_images)}")

    # Keep all minority images.
    selected = list(minority_images)

    chickpea_objects = sum(x[2] for x in selected)

    # Randomly select pure chickpea images until approximately
    # TARGET_CHICKPEA_OBJECTS are reached.
    random.shuffle(pure_chickpea_images)

    for item in pure_chickpea_images:
        if chickpea_objects >= TARGET_CHICKPEA_OBJECTS:
            break

        selected.append(item)
        chickpea_objects += item[2]

    print()
    print(f"Selected training images: {len(selected)}")
    print(f"Selected chickpea objects: {chickpea_objects}")

    # Create symlinks.
    for image, label_file, _ in selected:
        link_file(image, output_images / image.name)
        link_file(label_file, output_labels / label_file.name)

    return len(selected)


def copy_eval_split(split):
    source_images = SOURCE / split / "images"
    source_labels = SOURCE / split / "labels"

    output_images = OUTPUT / split / "images"
    output_labels = OUTPUT / split / "labels"

    output_images.mkdir(parents=True, exist_ok=True)
    output_labels.mkdir(parents=True, exist_ok=True)

    count = 0

    for image in source_images.iterdir():
        if not image.is_file():
            continue

        label_file = source_labels / f"{image.stem}.txt"

        if not label_file.exists():
            continue

        link_file(image, output_images / image.name)
        link_file(label_file, output_labels / label_file.name)

        count += 1

    print(f"{split}: {count} images")


def create_yaml():
    yaml_text = f"""path: {OUTPUT}

train: train/images
val: valid/images
test: test/images

nc: 43

names:
  - angle-gourd
  - basil seeds
  - beetroot seed
  - bitter-gourd
  - brown bean
  - cabbage
  - carrot
  - chia
  - chickpea
  - coffee beans
  - corn
  - cucumber seeds
  - egusi seeds
  - fennel
  - flax seeds
  - garlic seeds
  - grape seeds
  - hemp seeds
  - jackfruit
  - lotus seeds
  - mint seeds
  - muskmelon
  - mustard seeds
  - nigella seeds
  - oats seeds
  - onion seeds
  - peanut seeds
  - pinenut seeds
  - poppy seeds
  - potato seeds
  - pumpkin
  - radish seeds
  - rice seeds
  - sesame seeds
  - soya
  - split red lentils
  - sugar-pea
  - sunflower
  - watermelon seeds
  - waxgourd
  - wheat
  - wingbean
  - yardlong-bean
"""

    (OUTPUT / "data.yaml").write_text(yaml_text)


def main():
    print("Creating object-balanced YOLO dataset...")
    print()

    if OUTPUT.exists():
        print(f"Removing previous output: {OUTPUT}")
        shutil.rmtree(OUTPUT)

    OUTPUT.mkdir(parents=True)

    prepare_train()

    print()
    print("Copying validation and test splits unchanged...")
    copy_eval_split("valid")
    copy_eval_split("test")

    create_yaml()

    print()
    print("Dataset created successfully.")
    print(f"Output: {OUTPUT}")
    print(f"YAML:   {OUTPUT / 'data.yaml'}")


if __name__ == "__main__":
    main()
