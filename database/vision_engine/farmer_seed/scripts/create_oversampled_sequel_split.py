from pathlib import Path
import shutil
import random
import math

SEED = 42
MAX_REPEAT = 6

SOURCE = Path("processed/indian_ingredients")
OUTPUT = Path("processed/indian_ingredients_oversampled")

CLASS_NAMES = [
    "angle-gourd",
    "basil seeds",
    "beetroot seed",
    "bitter-gourd",
    "brown bean",
    "cabbage",
    "carrot",
    "chia",
    "chickpea",
    "coffee beans",
    "corn",
    "cucumber seeds",
    "egusi seeds",
    "fennel",
    "flax seeds",
    "garlic seeds",
    "grape seeds",
    "hemp seeds",
    "jackfruit",
    "lotus seeds",
    "mint seeds",
    "muskmelon",
    "mustard seeds",
    "nigella seeds",
    "oats seeds",
    "onion seeds",
    "peanut seeds",
    "pinenut seeds",
    "poppy seeds",
    "potato seeds",
    "pumpkin",
    "radish seeds",
    "rice seeds",
    "sesame seeds",
    "soya",
    "split red lentils",
    "sugar-pea",
    "sunflower",
    "watermelon seeds",
    "waxgourd",
    "wheat",
    "wingbean",
    "yardlong-bean",
]

random.seed(SEED)

print("Creating oversampled YOLO dataset...")
print()

if OUTPUT.exists():
    print(f"Removing previous output: {OUTPUT}")
    shutil.rmtree(OUTPUT)

# Read training image -> classes present in image
train_labels = SOURCE / "train" / "labels"
train_images = SOURCE / "train" / "images"

image_classes = {}

for label_file in train_labels.glob("*.txt"):
    classes = set()

    for line in label_file.read_text().splitlines():
        if line.strip():
            classes.add(int(float(line.split()[0])))

    image_classes[label_file.stem] = classes

class_image_counts = {i: 0 for i in range(len(CLASS_NAMES))}

for classes in image_classes.values():
    for cls in classes:
        class_image_counts[cls] += 1

# Target number of image occurrences for minority classes.
# We deliberately cap repetitions to avoid excessive overfitting.
TARGET_MINORITY_IMAGES = 80

print("Training image counts and repetition factors:")
print("-" * 55)

repeat_for_class = {}

for cls, name in enumerate(CLASS_NAMES):
    count = class_image_counts[cls]

    if cls == 8:  # chickpea
        repeat = 1
    else:
        repeat = min(MAX_REPEAT, max(1, math.ceil(TARGET_MINORITY_IMAGES / count)))

    repeat_for_class[cls] = repeat

    print(f"{name:24s} {count:5d} images -> {repeat}x")

print()

# Build training entries.
# Every original image is included at least once.
train_entries = []

for stem, classes in image_classes.items():

    repeat = 1

    minority_classes = [c for c in classes if c != 8]

    if minority_classes:
        repeat = max(repeat_for_class[c] for c in minority_classes)

    for r in range(repeat):
        train_entries.append((stem, r))

random.shuffle(train_entries)

# Create directories
for split in ["train", "valid", "test"]:
    (OUTPUT / split / "images").mkdir(parents=True, exist_ok=True)
    (OUTPUT / split / "labels").mkdir(parents=True, exist_ok=True)

# Copy/symlink training data
print(f"Original training images: {len(image_classes)}")
print(f"Oversampled training entries: {len(train_entries)}")

for index, (stem, repeat_id) in enumerate(train_entries):

    image_candidates = list(train_images.glob(stem + ".*"))

    if not image_candidates:
        print(f"WARNING: image not found for {stem}")
        continue

    image_source = image_candidates[0]
    label_source = train_labels / f"{stem}.txt"

    image_name = f"{index:05d}_{stem}{image_source.suffix}"
    label_name = f"{index:05d}_{stem}.txt"

    image_dest = OUTPUT / "train" / "images" / image_name
    label_dest = OUTPUT / "train" / "labels" / label_name

    image_dest.symlink_to(image_source.resolve())
    label_dest.symlink_to(label_source.resolve())

# Validation and test remain unchanged.
for split in ["valid", "test"]:

    source_images = SOURCE / split / "images"
    source_labels = SOURCE / split / "labels"

    for image_source in source_images.iterdir():
        if image_source.is_file():
            (OUTPUT / split / "images" / image_source.name).symlink_to(
                image_source.resolve()
            )

    for label_source in source_labels.glob("*.txt"):
        (OUTPUT / split / "labels" / label_source.name).symlink_to(
            label_source.resolve()
        )

# Create data.yaml
yaml_path = OUTPUT / "data.yaml"

with yaml_path.open("w") as f:
    f.write(f"path: {OUTPUT.resolve()}\n")
    f.write("train: train/images\n")
    f.write("val: valid/images\n")
    f.write("test: test/images\n")
    f.write(f"nc: {len(CLASS_NAMES)}\n")
    f.write("names:\n")

    for i, name in enumerate(CLASS_NAMES):
        f.write(f"  {i}: '{name}'\n")

print()
print("Dataset created successfully.")
print(f"Output: {OUTPUT.resolve()}")
print(f"Training entries: {len(train_entries)}")
print("Validation: 297 original images")
print("Test: 149 original images")
print(f"YAML: {yaml_path.resolve()}")
