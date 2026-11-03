
from pathlib import Path
from collections import defaultdict
import random

from PIL import Image, ImageDraw, ImageFont

# ==========================================
# CONFIGURATION
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = PROJECT_ROOT / "data" / "raw" / "dataset1"
OUTPUT_PATH = (
    PROJECT_ROOT / "results" / "visualizations" / "dataset1"
)

SPLIT = "train"
SAMPLES_PER_CLASS = 3
RANDOM_SEED = 42

# Pemetaan sementara berdasarkan distribusi
# objek pada Table 2, Scientific Data 2023.
# BELUM diverifikasi secara visual.
CLASS_NAMES = {
    0: "Empty Bunch",
    1: "Under-ripe",
    2: "Abnormal FFB",
    3: "Ripe",
    4: "Unripe",
    5: "Over Ripe",
}

COLORS = {
    0: "#808080",
    1: "#E6A700",
    2: "#A020F0",
    3: "#00A65A",
    4: "#007BFF",
    5: "#FF3333",
}

# ==========================================
# READ ANNOTATIONS
# ==========================================

def read_annotations(label_path):
    annotations = []

    for line in label_path.read_text(
        encoding="utf-8"
    ).splitlines():

        parts = line.strip().split()

        if not parts:
            continue

        if len(parts) != 5:
            print(f"Invalid annotation: {label_path}")
            continue

        class_id = int(parts[0])
        x, y, w, h = map(float, parts[1:])

        annotations.append(
            (class_id, x, y, w, h)
        )

    return annotations


# ==========================================
# DRAW BOUNDING BOXES
# ==========================================

def visualize_image(image_path, annotations, output_path):

    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    img_width, img_height = image.size

    font = ImageFont.load_default()

    for class_id, x, y, w, h in annotations:

        x1 = (x - w / 2) * img_width
        y1 = (y - h / 2) * img_height
        x2 = (x + w / 2) * img_width
        y2 = (y + h / 2) * img_height

        color = COLORS.get(class_id, "#FFFFFF")
        class_name = CLASS_NAMES.get(
            class_id, f"Unknown {class_id}"
        )

        label = f"{class_id}: {class_name}"

        draw.rectangle(
            [x1, y1, x2, y2],
            outline=color,
            width=3
        )

        text_bbox = draw.textbbox(
            (0, 0), label, font=font
        )

        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        label_y = max(0, y1 - text_height - 6)

        draw.rectangle(
            [
                x1,
                label_y,
                x1 + text_width + 8,
                label_y + text_height + 6,
            ],
            fill=color
        )

        draw.text(
            (x1 + 4, label_y + 3),
            label,
            fill="white",
            font=font
        )

    image.save(output_path)


# ==========================================
# MAIN
# ==========================================

def main():

    random.seed(RANDOM_SEED)

    split_path = DATASET_PATH / SPLIT

    if not split_path.exists():
        raise FileNotFoundError(
            f"Dataset folder not found: {split_path}"
        )

    OUTPUT_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    class_images = defaultdict(list)

    for label_path in sorted(split_path.glob("*.txt")):

        image_path = label_path.with_suffix(".jpg")

        if not image_path.exists():
            continue

        annotations = read_annotations(label_path)

        for class_id in set(
            item[0] for item in annotations
        ):
            class_images[class_id].append(
                (image_path, annotations)
            )

    selected = {}

    for class_id in sorted(CLASS_NAMES):

        candidates = class_images[class_id]

        if not candidates:
            print(f"No images for class {class_id}")
            continue

        samples = random.sample(
            candidates,
            min(SAMPLES_PER_CLASS, len(candidates))
        )

        selected[class_id] = samples

    total_saved = 0

    for class_id, samples in selected.items():

        class_output = OUTPUT_PATH / f"class_{class_id}"
        class_output.mkdir(exist_ok=True)

        for image_path, annotations in samples:

            output_file = class_output / image_path.name

            visualize_image(
                image_path,
                annotations,
                output_file
            )

            total_saved += 1

        print(
            f"Class {class_id} "
            f"({CLASS_NAMES[class_id]}): "
            f"{len(samples)} images"
        )

    print("\nVisualization completed.")
    print(f"Total images saved: {total_saved}")
    print(f"Output directory: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
