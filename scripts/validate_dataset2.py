
from pathlib import Path
from collections import defaultdict
from hashlib import sha256
from PIL import Image, ImageDraw, ImageFont
import random

ROOT = Path("data/raw/dataset2/yolov8")
OUTPUT = Path("results/visualizations/dataset2")

CLASSES = {
    0: "Abnormal",
    1: "Flower",
    2: "Ripe",
    3: "Underripe",
    4: "Unripe",
}

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
SPLITS = ("train", "valid", "test")
rng = random.Random(42)

hashes = defaultdict(list)
samples = defaultdict(list)
broken = []
image_counts = {}
duplicate_groups = []

print("=== DATASET 2 VALIDATION ===")

for split in SPLITS:
    images_dir = ROOT / split / "images"
    labels_dir = ROOT / split / "labels"

    images = sorted(
        p for p in images_dir.iterdir()
        if p.suffix.lower() in EXTENSIONS
    )
    image_counts[split] = len(images)

    print(f"\nChecking {split}: {len(images)} images")

    for image_path in images:
        try:
            # Verify image integrity.
            with Image.open(image_path) as im:
                im.verify()

            with Image.open(image_path) as im:
                width, height = im.size

            # Hash file content to detect exact duplicates.
            digest = sha256(image_path.read_bytes()).hexdigest()
            hashes[digest].append((split, image_path))

            label_path = labels_dir / (image_path.stem + ".txt")

            if not label_path.exists():
                continue

            for line in label_path.read_text(
                encoding="utf-8-sig"
            ).splitlines():
                parts = line.split()

                if len(parts) != 5:
                    continue

                try:
                    class_id = int(parts[0])
                    coords = tuple(map(float, parts[1:]))
                except ValueError:
                    continue

                if class_id in CLASSES:
                    samples[class_id].append(
                        (image_path, width, height, coords)
                    )

        except Exception as exc:
            broken.append((str(image_path), str(exc)))

# Identify exact duplicate images.
for paths in hashes.values():
    if len(paths) > 1:
        duplicate_groups.append(paths)

cross_split = [
    group for group in duplicate_groups
    if len({split for split, _ in group}) > 1
]

print("\n=== INTEGRITY RESULTS ===")
print("Images per split:", image_counts)
print("Broken images:", len(broken))
print("Exact duplicate groups:", len(duplicate_groups))
print("Cross-split duplicate groups:", len(cross_split))

for path, error in broken[:10]:
    print("BROKEN:", path, error)

for group in cross_split[:10]:
    print("CROSS-SPLIT DUPLICATE:")
    for split, path in group:
        print(" ", split, path.name)

# Create sample visualizations.
print("\n=== VISUALIZATIONS ===")

for class_id, class_name in CLASSES.items():
    folder = OUTPUT / f"class_{class_id}"
    folder.mkdir(parents=True, exist_ok=True)

    # Prefer different images for each class.
    unique = {}
    for item in samples[class_id]:
        unique.setdefault(str(item[0]), item)

    selected = rng.sample(
        list(unique.values()),
        min(3, len(unique))
    )

    for index, (path, width, height, coords) in enumerate(
        selected, start=1
    ):
        with Image.open(path) as original:
            im = original.convert("RGB")

        draw = ImageDraw.Draw(im)

        xc, yc, bw, bh = coords
        x1 = (xc - bw / 2) * width
        y1 = (yc - bh / 2) * height
        x2 = (xc + bw / 2) * width
        y2 = (yc + bh / 2) * height

        draw.rectangle(
            [x1, y1, x2, y2],
            outline="red",
            width=4
        )

        draw.text(
            (max(0, x1), max(0, y1 - 15)),
            f"{class_id}: {class_name}",
            fill="yellow",
            stroke_width=2,
            stroke_fill="black"
        )

        destination = folder / f"sample_{index}.jpg"
        im.save(destination, quality=95)

    print(
        f"Class {class_id} ({class_name}): "
        f"{len(unique)} candidate images, "
        f"{len(selected)} samples saved"
    )

print("\nFinished.")
print("Visualizations saved to:", OUTPUT)
