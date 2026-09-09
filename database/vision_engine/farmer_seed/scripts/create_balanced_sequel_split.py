from pathlib import Path
from collections import defaultdict
import random
import shutil

BASE = Path(
    "/home/mousumi/Documents/final project/jivanya/database/vision_engine/farmer_seed"
)

SOURCE = BASE / "processed" / "indian_ingredients"
OUTPUT = BASE / "processed" / "indian_ingredients_balanced"

SEED = 42
random.seed(SEED)

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

RATIOS = {
    "train": 0.70,
    "valid": 0.15,
    "test": 0.15,
}


def get_classes(label_file):
    classes = set()

    if label_file.exists():
        for line in label_file.read_text().splitlines():
            parts = line.strip().split()

            if parts:
                classes.add(int(float(parts[0])))

    return classes


def main():

    print("Creating corrected balanced Sequel Farmer split...")
    print()

    # ---------------------------------------------------------
    # Collect all images
    # ---------------------------------------------------------
    images = []

    for split in ["train", "valid", "test"]:

        image_dir = SOURCE / split / "images"
        label_dir = SOURCE / split / "labels"

        for image in image_dir.iterdir():

            if not image.is_file():
                continue

            label = label_dir / f"{image.stem}.txt"

            images.append({
                "image": image,
                "label": label,
                "classes": get_classes(label),
            })

    total = len(images)

    print(f"Total images found: {total}")

    # ---------------------------------------------------------
    # Target split sizes
    # ---------------------------------------------------------
    targets = {
        "train": round(total * 0.70),
        "valid": round(total * 0.15),
        "test": 0,
    }

    targets["test"] = total - targets["train"] - targets["valid"]

    print()
    print("Target split sizes:")

    for split in targets:
        print(f"{split}: {targets[split]}")

    # ---------------------------------------------------------
    # Count images containing each class
    # ---------------------------------------------------------
    class_images = defaultdict(list)

    for item in images:
        for cls in item["classes"]:
            class_images[cls].append(item)

    print()
    print("Original class image counts:")

    for cls, name in enumerate(CLASS_NAMES):
        print(f"{cls:2d} {name:<20} {len(class_images[cls])}")

    # ---------------------------------------------------------
    # Desired class counts per split
    # ---------------------------------------------------------
    desired = {
        "train": {},
        "valid": {},
        "test": {},
    }

    for cls in range(len(CLASS_NAMES)):

        count = len(class_images[cls])

        if count == 0:
            continue

        desired["valid"][cls] = max(1, round(count * 0.15))
        desired["test"][cls] = max(1, round(count * 0.15))

        desired["train"][cls] = max(
            1,
            count
            - desired["valid"][cls]
            - desired["test"][cls]
        )

    # ---------------------------------------------------------
    # Assignment containers
    # ---------------------------------------------------------
    assignments = {
        "train": [],
        "valid": [],
        "test": [],
    }

    assigned = set()

    # Current class counts
    current = {
        "train": defaultdict(int),
        "valid": defaultdict(int),
        "test": defaultdict(int),
    }

    # ---------------------------------------------------------
    # First guarantee:
    # Every class gets at least one image in every split.
    #
    # Classes with fewer images than 3 are handled separately.
    # ---------------------------------------------------------
    print()
    print("Guaranteeing class coverage...")

    classes_by_rarity = sorted(
        range(len(CLASS_NAMES)),
        key=lambda c: len(class_images[c])
    )

    for cls in classes_by_rarity:

        candidates = [
            item
            for item in class_images[cls]
            if id(item) not in assigned
        ]

        random.shuffle(candidates)

        if len(class_images[cls]) < 3:
            continue

        for split in ["valid", "test", "train"]:

            if current[split][cls] >= 1:
                continue

            available = [
                item
                for item in candidates
                if id(item) not in assigned
                and len(assignments[split]) < targets[split]
            ]

            if not available:
                continue

            # Prefer an image with the fewest other classes.
            item = min(
                available,
                key=lambda x: len(x["classes"])
            )

            assignments[split].append(item)
            assigned.add(id(item))

            for c in item["classes"]:
                current[split][c] += 1

    # ---------------------------------------------------------
    # Greedy assignment of remaining images.
    #
    # Images containing rare classes are processed first.
    # Each image is placed into the split with the largest
    # unmet class demand.
    # ---------------------------------------------------------
    remaining = [
        item
        for item in images
        if id(item) not in assigned
    ]

    random.shuffle(remaining)

    remaining.sort(
        key=lambda item: (
            sum(
                1 / max(1, len(class_images[c]))
                for c in item["classes"]
            )
        ),
        reverse=True
    )

    for item in remaining:

        available_splits = [
            split
            for split in targets
            if len(assignments[split]) < targets[split]
        ]

        if not available_splits:
            break

        best_split = None
        best_score = None

        for split in available_splits:

            score = 0.0

            for cls in item["classes"]:

                target = desired[split].get(cls, 0)
                have = current[split][cls]

                deficit = max(0, target - have)

                # Strongly prefer splits that still need this class.
                score += deficit * 100

                # Small preference for maintaining total split size.
                remaining_capacity = (
                    targets[split] - len(assignments[split])
                )

                score += remaining_capacity / targets[split]

            if best_score is None or score > best_score:
                best_score = score
                best_split = split

        assignments[best_split].append(item)
        assigned.add(id(item))

        for cls in item["classes"]:
            current[best_split][cls] += 1

    # ---------------------------------------------------------
    # Final size check
    # ---------------------------------------------------------
    print()
    print("Final split sizes:")

    for split in targets:
        print(
            f"{split}: "
            f"{len(assignments[split])} "
            f"/ target {targets[split]}"
        )

    if sum(len(v) for v in assignments.values()) != total:
        raise RuntimeError(
            "ERROR: Some images were not assigned."
        )

    # ---------------------------------------------------------
    # Remove only the NEW balanced dataset
    # ---------------------------------------------------------
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)

    # ---------------------------------------------------------
    # Create directories
    # ---------------------------------------------------------
    for split in targets:

        (OUTPUT / split / "images").mkdir(
            parents=True,
            exist_ok=True
        )

        (OUTPUT / split / "labels").mkdir(
            parents=True,
            exist_ok=True
        )

    # ---------------------------------------------------------
    # Create symbolic links
    # ---------------------------------------------------------
    for split, items in assignments.items():

        for item in items:

            image_destination = (
                OUTPUT / split / "images" / item["image"].name
            )

            label_destination = (
                OUTPUT / split / "labels" / item["label"].name
            )

            image_destination.symlink_to(
                item["image"].resolve()
            )

            if item["label"].exists():
                label_destination.symlink_to(
                    item["label"].resolve()
                )

    # ---------------------------------------------------------
    # Create data.yaml
    # ---------------------------------------------------------
    yaml_lines = [
        f"path: {OUTPUT}",
        "",
        "train: train/images",
        "val: valid/images",
        "test: test/images",
        "",
        "nc: 43",
        "",
        "names:",
    ]

    for name in CLASS_NAMES:
        yaml_lines.append(f"  - {name}")

    (OUTPUT / "data.yaml").write_text(
        "\n".join(yaml_lines) + "\n"
    )

    print()
    print("Corrected balanced split created successfully.")
    print()
    print(f"Output: {OUTPUT}")
    print()
    print("IMPORTANT: Verify the class distribution before training.")


if __name__ == "__main__":
    main()
