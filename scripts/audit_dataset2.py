
from pathlib import Path
from collections import Counter

DATASET = Path("data/raw/dataset2/yolov8")
SPLITS = ["train", "valid", "test"]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

total_images = 0
total_labels = 0
total_objects = 0
total_classes = Counter()
total_warnings = 0

for split in SPLITS:
    images_dir = DATASET / split / "images"
    labels_dir = DATASET / split / "labels"

    images = {
        p.stem: p
        for p in images_dir.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    }
    labels = {
        p.stem: p
        for p in labels_dir.glob("*.txt")
    }

    class_counts = Counter()
    warnings = []

    for stem in images.keys() - labels.keys():
        warnings.append(f"Missing label: {stem}")

    for stem in labels.keys() - images.keys():
        warnings.append(f"Missing image: {stem}")

    for label_file in labels.values():
        for line_num, line in enumerate(
            label_file.read_text(encoding="utf-8-sig").splitlines(),
            start=1
        ):
            if not line.strip():
                continue

            parts = line.split()

            if len(parts) != 5:
                warnings.append(
                    f"{label_file.name}:{line_num} invalid column count"
                )
                continue

            try:
                class_value = float(parts[0])
                coords = [float(v) for v in parts[1:]]
            except ValueError:
                warnings.append(
                    f"{label_file.name}:{line_num} non-numeric value"
                )
                continue

            if not class_value.is_integer() or class_value < 0:
                warnings.append(
                    f"{label_file.name}:{line_num} invalid class ID"
                )
                continue

            class_id = int(class_value)
            x, y, w, h = coords

            if not (
                0 <= x <= 1 and 0 <= y <= 1
                and 0 < w <= 1 and 0 < h <= 1
                and x - w / 2 >= -1e-6
                and y - h / 2 >= -1e-6
                and x + w / 2 <= 1 + 1e-6
                and y + h / 2 <= 1 + 1e-6
            ):
                warnings.append(
                    f"{label_file.name}:{line_num} invalid bounding box"
                )

            class_counts[class_id] += 1

    objects = sum(class_counts.values())

    total_images += len(images)
    total_labels += len(labels)
    total_objects += objects
    total_classes.update(class_counts)
    total_warnings += len(warnings)

    print(f"\n{'=' * 50}")
    print(f"SPLIT: {split.upper()}")
    print(f"Images  : {len(images)}")
    print(f"Labels  : {len(labels)}")
    print(f"Objects : {objects}")
    print(f"Classes : {dict(sorted(class_counts.items()))}")
    print(f"Warnings: {len(warnings)}")

    for warning in warnings[:10]:
        print(f"  WARNING: {warning}")

print(f"\n{'=' * 50}")
print("TOTAL DATASET 2")
print(f"Images  : {total_images}")
print(f"Labels  : {total_labels}")
print(f"Objects : {total_objects}")
print(f"Classes : {dict(sorted(total_classes.items()))}")
print(f"Warnings: {total_warnings}")
