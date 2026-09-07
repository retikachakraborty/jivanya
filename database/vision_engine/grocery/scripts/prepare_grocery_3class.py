from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw" / "grocery_detection"
OUT = ROOT / "processed" / "grocery_detection_3class"

KEEP = {0: 0, 1: 1, 3: 2}

for split in ["train", "valid", "test"]:
    src_images = RAW / split / "images"
    src_labels = RAW / split / "labels"
    dst_images = OUT / split / "images"
    dst_labels = OUT / split / "labels"

    dst_images.mkdir(parents=True, exist_ok=True)
    dst_labels.mkdir(parents=True, exist_ok=True)

    for image in src_images.iterdir():
        if not image.is_file():
            continue

        label = src_labels / f"{image.stem}.txt"

        if not label.exists():
            continue

        output_lines = []

        for line in label.read_text().splitlines():
            parts = line.split()

            if not parts:
                continue

            cls = int(parts[0])

            if cls not in KEEP:
                continue

            coords = list(map(float, parts[1:]))

            if len(coords) >= 6 and len(coords) % 2 == 0:
                xs = coords[0::2]
                ys = coords[1::2]

                xmin, xmax = min(xs), max(xs)
                ymin, ymax = min(ys), max(ys)

                xc = (xmin + xmax) / 2
                yc = (ymin + ymax) / 2
                w = xmax - xmin
                h = ymax - ymin

                output_lines.append(
                    f"{KEEP[cls]} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}"
                )

            elif len(coords) == 4:
                output_lines.append(
                    f"{KEEP[cls]} " +
                    " ".join(f"{v:.6f}" for v in coords)
                )

        if output_lines:
            shutil.copy2(image, dst_images / image.name)
            (dst_labels / label.name).write_text(
                "\n".join(output_lines) + "\n"
            )

(OUT / "data.yaml").write_text(
    """train: ../train/images
val: ../valid/images
test: ../test/images

nc: 3
names: ['atta', 'maida', 'vermicelli']
""",
    encoding="utf-8"
)

print("3-class Grocery Detection dataset created.")
print("Classes: atta, maida, vermicelli")
print(f"Output: {OUT}")
