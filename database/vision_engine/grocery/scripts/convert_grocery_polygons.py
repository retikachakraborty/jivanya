from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw" / "grocery_detection"
OUT = ROOT / "processed" / "grocery_detection"

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

        shutil.copy2(image, dst_images / image.name)

        if not label.exists():
            continue

        output_lines = []

        for line in label.read_text().splitlines():
            parts = line.split()

            if not parts:
                continue

            cls = int(parts[0])
            coords = list(map(float, parts[1:]))

            # Polygon: class + x1 y1 x2 y2 ... xn yn
            if len(coords) >= 6 and len(coords) % 2 == 0:
                xs = coords[0::2]
                ys = coords[1::2]

                xmin = min(xs)
                xmax = max(xs)
                ymin = min(ys)
                ymax = max(ys)

                x_center = (xmin + xmax) / 2
                y_center = (ymin + ymax) / 2
                width = xmax - xmin
                height = ymax - ymin

                output_lines.append(
                    f"{cls} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
                )

            # Already a normal YOLO bounding box
            elif len(coords) == 4:
                output_lines.append(line)

        (dst_labels / label.name).write_text(
            "\n".join(output_lines) + ("\n" if output_lines else "")
        )

yaml = OUT / "data.yaml"
yaml.write_text(
    """train: ../train/images
val: ../valid/images
test: ../test/images

nc: 4
names: ['atta', 'maida', 'suji', 'vermicelli']
""",
    encoding="utf-8"
)

print("Polygon → bounding-box conversion completed.")
print("Classes: atta, maida, suji, vermicelli")
print(f"Output: {OUT}")
