from pathlib import Path

BASE = Path("/home/mousumi/Documents/final project/jivanya/database/vision_engine/farmer_seed")
LABEL_ROOT = BASE / "processed" / "indian_ingredients"

splits = ["train", "valid", "test"]

converted = 0
kept = 0

for split in splits:
    label_dir = LABEL_ROOT / split / "labels"

    for label_file in label_dir.glob("*.txt"):
        new_lines = []

        for line in label_file.read_text().splitlines():
            parts = line.strip().split()

            if not parts:
                continue

            # YOLO detection format:
            # class x_center y_center width height
            if len(parts) == 5:
                cls, xc, yc, w, h = map(float, parts)

                x1 = xc - w / 2
                y1 = yc - h / 2
                x2 = xc + w / 2
                y2 = yc + h / 2

                # Convert bounding box to rectangular segmentation polygon
                polygon = [
                    cls,
                    x1, y1,
                    x2, y1,
                    x2, y2,
                    x1, y2
                ]

                new_lines.append(
                    " ".join(f"{v:.10f}" for v in polygon)
                )
                converted += 1

            else:
                # Existing segmentation polygon: keep unchanged
                new_lines.append(line)
                kept += 1

        label_file.write_text("\n".join(new_lines) + "\n")

print("Cleaning completed successfully.")
print(f"Bounding-box annotations converted: {converted}")
print(f"Existing segmentation annotations kept: {kept}")
