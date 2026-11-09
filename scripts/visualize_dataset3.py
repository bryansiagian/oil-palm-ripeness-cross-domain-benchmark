
from pathlib import Path
from collections import defaultdict
import random

from PIL import Image, ImageDraw, ImageFont

# ==========================================
# CONFIGURATION
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    PROJECT_ROOT
    / "MunirahRosbi-Outdoor-Tenera-Oil-Palm-Fruit-Image-b27ea70"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "results"
    / "visualizations"
    / "dataset3"
)

SPLITS = {
    "Train": DATASET_PATH / "FFBtrain",
    "Test": DATASET_PATH / "FFBtest",
}

SAMPLES_PER_CLASS = 3
RANDOM_SEED = 42

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_class_name(folder_name):

    for prefix in ["Train", "Test"]:

        if folder_name.startswith(prefix):
            return folder_name[len(prefix):]

    return folder_name


def visualize_image(image_path, class_name, split, output_path):

    image = Image.open(image_path).convert("RGB")

    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    label = f"{split} | Class: {class_name}"

    text_bbox = draw.textbbox((0, 0), label, font=font)

    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    draw.rectangle(
        [0, 0, text_width + 16, text_height + 14],
        fill="#00875A"
    )

    draw.text(
        (8, 7),
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

    total_saved = 0

    print("=" * 55)
    print("DATASET 3 - IMAGE VISUALIZATION")
    print("=" * 55)

    for split, split_path in SPLITS.items():

        if not split_path.exists():
            print(f"Folder not found: {split_path}")
            continue

        print(f"\n=== {split.upper()} ===")

        class_images = defaultdict(list)

        for class_folder in sorted(split_path.iterdir()):

            if not class_folder.is_dir():
                continue

            class_name = get_class_name(class_folder.name)

            images = sorted(
                path for path in class_folder.rglob("*")
                if path.is_file()
                and path.suffix.lower() in IMAGE_EXTENSIONS
            )

            class_images[class_name].extend(images)

        for class_name, candidates in sorted(class_images.items()):

            if not candidates:
                print(f"No images for class: {class_name}")
                continue

            samples = random.sample(
                candidates,
                min(SAMPLES_PER_CLASS, len(candidates))
            )

            class_output = (
                OUTPUT_PATH
                / split.lower()
                / class_name.lower()
            )

            class_output.mkdir(
                parents=True,
                exist_ok=True
            )

            for index, image_path in enumerate(samples, start=1):

                output_file = (
                    class_output
                    / f"{class_name.lower()}_sample_{index}.jpg"
                )

                visualize_image(
                    image_path,
                    class_name,
                    split,
                    output_file
                )

                total_saved += 1

            print(
                f"{class_name:<15}: "
                f"{len(samples)} images visualized"
            )

    print("\nVisualization completed.")
    print(f"Total images saved: {total_saved}")
    print(f"Output directory: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
