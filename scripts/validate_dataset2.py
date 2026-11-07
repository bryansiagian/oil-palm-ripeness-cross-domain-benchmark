
from pathlib import Path
from collections import defaultdict
from hashlib import sha256
from PIL import Image, ImageDraw, ImageFont
import random

# ============================================================
# CONFIGURATION
# ============================================================

ROOT = Path("data/raw/dataset2/yolov8")
OUTPUT = Path("results/visualizations/dataset2")

CLASSES = {
    0: "Abnormal",
    1: "Flower",
    2: "Ripe",
    3: "Underripe",
    4: "Unripe",
}

COLORS = {
    0: "#FF4444",
    1: "#FFA500",
    2: "#22BB66",
    3: "#AA55FF",
    4: "#0088FF",
}

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
SPLITS = ("train", "valid", "test")
SAMPLES_PER_CLASS = 3

rng = random.Random(42)

hashes = defaultdict(list)
samples = defaultdict(dict)
broken = []
image_counts = {}

# ============================================================
# HELPERS
# ============================================================

def load_annotations(label_path):
    """Read all YOLO bounding boxes from one label file."""
    annotations = []

    if not label_path.exists():
        return annotations

    lines = label_path.read_text(
        encoding="utf-8-sig"
    ).splitlines()

    for line_num, line in enumerate(lines, start=1):
        parts = line.split()

        if not parts:
            continue

        if len(parts) != 5:
            print(
                f"WARNING: Invalid annotation at "
                f"{label_path}:{line_num}"
            )
            continue

        try:
            class_id = int(parts[0])
            x, y, w, h = map(float, parts[1:])
        except ValueError:
            print(
                f"WARNING: Non-numeric annotation at "
                f"{label_path}:{line_num}"
            )
            continue

        if class_id not in CLASSES:
            print(
                f"WARNING: Unknown class {class_id} "
                f"at {label_path}:{line_num}"
            )
            continue

        annotations.append((class_id, x, y, w, h))

    return annotations


def draw_annotations(image_path, annotations):
    """Draw ALL bounding boxes on the selected image."""

    with Image.open(image_path) as original:
        image = original.convert("RGB")

    draw = ImageDraw.Draw(image)
    width, height = image.size

    try:
        font = ImageFont.truetype("arial.ttf", 17)
    except OSError:
        font = ImageFont.load_default()

    for class_id, xc, yc, bw, bh in annotations:
        x1 = (xc - bw / 2) * width
        y1 = (yc - bh / 2) * height
        x2 = (xc + bw / 2) * width
        y2 = (yc + bh / 2) * height

        color = COLORS[class_id]
        label = f"{class_id}: {CLASSES[class_id]}"

        # Draw bounding box.
        draw.rectangle(
            [x1, y1, x2, y2],
            outline=color,
            width=3
        )

        # Draw readable label background.
        left, top, right, bottom = draw.textbbox(
            (0, 0),
            label,
            font=font
        )

        text_width = right - left
        text_height = bottom - top

        label_x = max(0, int(x1))
        label_y = max(0, int(y1) - text_height - 8)

        label_x = min(
            label_x,
            max(0, width - text_width - 8)
        )

        draw.rectangle(
            [
                label_x,
                label_y,
                label_x + text_width + 8,
                label_y + text_height + 6
            ],
            fill=color
        )

        draw.text(
            (label_x + 4, label_y + 3),
            label,
            fill="white",
            font=font
        )

    return image


# ============================================================
# STEP 1: DATASET INTEGRITY VALIDATION
# ============================================================

print("=== DATASET 2 VALIDATION ===")

for split in SPLITS:
    images_dir = ROOT / split / "images"
    labels_dir = ROOT / split / "labels"

    if not images_dir.is_dir():
        raise FileNotFoundError(images_dir)

    if not labels_dir.is_dir():
        raise FileNotFoundError(labels_dir)

    images = sorted(
        p for p in images_dir.iterdir()
        if p.is_file()
        and p.suffix.lower() in EXTENSIONS
    )

    image_counts[split] = len(images)

    print(f"\nChecking {split}: {len(images)} images")

    for image_path in images:
        try:
            # Check image integrity.
            with Image.open(image_path) as im:
                im.verify()

            # Detect byte-identical duplicates.
            digest = sha256(
                image_path.read_bytes()
            ).hexdigest()

            hashes[digest].append(
                (split, image_path)
            )

            label_path = (
                labels_dir / f"{image_path.stem}.txt"
            )

            annotations = load_annotations(label_path)

            # Register this image for each class it contains.
            present_classes = {
                annotation[0]
                for annotation in annotations
            }

            for class_id in present_classes:
                samples[class_id][str(image_path)] = (
                    image_path,
                    label_path
                )

        except Exception as exc:
            broken.append(
                (str(image_path), str(exc))
            )

# ============================================================
# STEP 2: DUPLICATE DETECTION
# ============================================================

duplicate_groups = [
    paths
    for paths in hashes.values()
    if len(paths) > 1
]

cross_split_duplicates = [
    group
    for group in duplicate_groups
    if len({split for split, _ in group}) > 1
]

print("\n=== INTEGRITY RESULTS ===")
print("Images per split:", image_counts)
print("Broken images:", len(broken))
print("Exact duplicate groups:", len(duplicate_groups))
print(
    "Cross-split duplicate groups:",
    len(cross_split_duplicates)
)

for path, error in broken[:10]:
    print("BROKEN:", path, error)

for group in cross_split_duplicates[:10]:
    print("CROSS-SPLIT DUPLICATE:")
    for split, path in group:
        print(" ", split, path.name)

# ============================================================
# STEP 3: VISUALIZE ALL BOUNDING BOXES
# ============================================================

print("\n=== VISUALIZATIONS ===")

for class_id, class_name in CLASSES.items():
    folder = OUTPUT / f"class_{class_id}"
    folder.mkdir(parents=True, exist_ok=True)

    # Remove previous generated samples to avoid confusion.
    for old_file in folder.glob("sample_*.jpg"):
        old_file.unlink()

    candidates = list(samples[class_id].values())

    selected = rng.sample(
        candidates,
        min(SAMPLES_PER_CLASS, len(candidates))
    )

    for index, (image_path, label_path) in enumerate(
        selected,
        start=1
    ):
        # Read ALL annotations for this image.
        annotations = load_annotations(label_path)

        # Draw ALL boxes, including other classes.
        visualized = draw_annotations(
            image_path,
            annotations
        )

        destination = folder / f"sample_{index}.jpg"

        visualized.save(
            destination,
            quality=95
        )

    print(
        f"Class {class_id} ({class_name}): "
        f"{len(candidates)} candidate images, "
        f"{len(selected)} samples saved"
    )

print("\nFinished.")
print("Visualizations saved to:", OUTPUT)
