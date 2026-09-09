from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw" / "grocery_detection"
OUT = ROOT / "processed" / "grocery_detection"

CLASSES = ["atta", "maida", "suji", "vermicelli"]

for split in ["train", "valid", "test"]:
    src_img = RAW / split / "images"
    src_lbl = RAW / split / "labels"
    dst_img = OUT / split / "images"
    dst_lbl = OUT / split / "labels"

    dst_img.mkdir(parents=True, exist_ok=True)
    dst_lbl.mkdir(parents=True, exist_ok=True)

    for img in src_img.iterdir():
        if img.is_file():
            label = src_lbl / f"{img.stem}.txt"

            if not label.exists():
                continue

            shutil.copy2(img, dst_img / img.name)
            shutil.copy2(label, dst_lbl / label.name)

yaml = OUT / "data.yaml"
yaml.write_text(
    f"""train: ../train/images
val: ../valid/images
test: ../test/images

nc: {len(CLASSES)}
names: {CLASSES}
""",
    encoding="utf-8"
)

print("Processed Grocery Detection dataset created.")
print(f"Classes: {len(CLASSES)}")
print(f"Output: {OUT}")
