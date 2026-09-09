from pathlib import Path

BASE = Path("processed/indian_ingredients_balanced")

names = [
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


def count_classes(split):
    counts = [0] * len(names)
    label_dir = BASE / split / "labels"

    for label_file in label_dir.glob("*.txt"):
        classes_in_image = set()

        for line in label_file.read_text().splitlines():
            parts = line.strip().split()

            if parts:
                classes_in_image.add(int(float(parts[0])))

        for cls in classes_in_image:
            if 0 <= cls < len(names):
                counts[cls] += 1

    return counts


print("\nCLASS DISTRIBUTION")
print("=" * 75)
print(f"{'Class':<20} {'Train':>8} {'Valid':>8} {'Test':>8}")
print("-" * 75)

train = count_classes("train")
valid = count_classes("valid")
test = count_classes("test")

for i, name in enumerate(names):
    print(
        f"{name:<20} "
        f"{train[i]:>8} "
        f"{valid[i]:>8} "
        f"{test[i]:>8}"
    )

print("-" * 75)

print("\nImages in each split:")
for split in ["train", "valid", "test"]:
    count = len(list((BASE / split / "images").glob("*")))
    print(f"{split}: {count}")

print("\nClasses missing from validation:")
for i, name in enumerate(names):
    if valid[i] == 0:
        print(f"  {i}: {name}")

print("\nClasses missing from test:")
for i, name in enumerate(names):
    if test[i] == 0:
        print(f"  {i}: {name}")

print("\nVerification completed.")
