
import json
import math
import shutil
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_ROOT = PROJECT_ROOT / "data" / "raw"
PROCESSED_ROOT = PROJECT_ROOT / "data" / "processed"
REPORT_ROOT = PROJECT_ROOT / "results" / "preprocessing"

CONFIG_PATH = PROJECT_ROOT / "configs" / "class_mapping.yaml"

SPLITS = ("train", "valid", "test")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}

BBOX_TOLERANCE = 1e-6


def load_config():
    """Load and validate the shared class mapping."""

    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if config["nc"] != 2:
        raise ValueError("Expected exactly two target classes.")

    if config["names"] != {0: "Unripe", 1: "Ripe"}:
        raise ValueError("Invalid target class taxonomy.")

    return config


def collect_files(directory, extensions):
    """Collect files indexed by filename stem."""

    if not directory.is_dir():
        raise FileNotFoundError(
            f"Directory not found: {directory}"
        )

    files = {}

    for path in sorted(directory.iterdir()):
        if not path.is_file():
            continue

        if path.suffix.lower() not in extensions:
            continue

        if path.stem in files:
            raise ValueError(
                f"Duplicate filename stem: {path}"
            )

        files[path.stem] = path

    return files


def validate_image(image_path):
    """Check whether an image can be decoded."""

    with Image.open(image_path) as image:
        image.verify()

    with Image.open(image_path) as image:
        image.load()

        if image.width <= 0 or image.height <= 0:
            raise ValueError(
                f"Invalid image dimensions: {image_path}"
            )


def parse_annotation(line, label_path, line_number):
    """Parse and validate one YOLO annotation."""

    parts = line.split()

    location = f"{label_path}:{line_number}"

    if len(parts) != 5:
        raise ValueError(
            f"Expected five annotation fields: {location}"
        )

    try:
        class_id = int(parts[0])

        x_center, y_center, width, height = map(
            float, parts[1:]
        )

    except ValueError as error:
        raise ValueError(
            f"Invalid annotation values: {location}"
        ) from error

    coordinates = (
        x_center,
        y_center,
        width,
        height,
    )

    if class_id < 0:
        raise ValueError(
            f"Negative class ID: {location}"
        )

    if not all(math.isfinite(v) for v in coordinates):
        raise ValueError(
            f"Non-finite coordinates: {location}"
        )

    if not all(0 <= v <= 1 for v in coordinates):
        raise ValueError(
            f"Coordinates outside normalized range: {location}"
        )

    if width <= 0 or height <= 0:
        raise ValueError(
            f"Invalid bounding-box size: {location}"
        )

    x_min = x_center - width / 2
    y_min = y_center - height / 2

    x_max = x_center + width / 2
    y_max = y_center + height / 2

    if (
        x_min < -BBOX_TOLERANCE
        or y_min < -BBOX_TOLERANCE
        or x_max > 1 + BBOX_TOLERANCE
        or y_max > 1 + BBOX_TOLERANCE
    ):
        raise ValueError(
            f"Bounding box exceeds image boundaries: {location}"
        )

    return class_id, parts[1:]


def process_label(label_path, class_mapping):
    """Filter and remap annotations to the target taxonomy."""

    processed_lines = []

    original_counts = Counter()
    target_counts = Counter()

    removed_objects = 0

    lines = label_path.read_text(
        encoding="utf-8"
    ).splitlines()

    for line_number, line in enumerate(lines, start=1):

        if not line.strip():
            continue

        original_id, coordinates = parse_annotation(
            line,
            label_path,
            line_number,
        )

        if original_id not in class_mapping:
            raise ValueError(
                f"Unknown class ID {original_id}: "
                f"{label_path}:{line_number}"
            )

        original_counts[original_id] += 1

        target_id = class_mapping[original_id]

        if target_id is None:
            removed_objects += 1
            continue

        if target_id not in (0, 1):
            raise ValueError(
                f"Invalid target class ID: {target_id}"
            )

        target_counts[target_id] += 1

        # Preserve the original coordinate values.
        new_line = " ".join(
            [str(target_id)] + coordinates
        )

        processed_lines.append(new_line)

    return {
        "lines": processed_lines,
        "original_counts": original_counts,
        "target_counts": target_counts,
        "removed_objects": removed_objects,
    }


def process_split(
    image_directory,
    label_directory,
    output_directory,
    class_mapping,
):
    """Preprocess one dataset split."""

    images = collect_files(
        image_directory,
        IMAGE_EXTENSIONS,
    )

    labels = collect_files(
        label_directory,
        {".txt"},
    )

    if not images:
        raise ValueError(
            f"No images found: {image_directory}"
        )

    missing_labels = sorted(
        set(images) - set(labels)
    )

    missing_images = sorted(
        set(labels) - set(images)
    )

    if missing_labels or missing_images:
        raise ValueError(
            "Image-label correspondence failed.\n"
            f"Missing labels: {len(missing_labels)}\n"
            f"Examples: {missing_labels[:5]}\n"
            f"Missing images: {len(missing_images)}\n"
            f"Examples: {missing_images[:5]}"
        )

    output_images = output_directory / "images"
    output_labels = output_directory / "labels"

    output_images.mkdir(parents=True, exist_ok=True)
    output_labels.mkdir(parents=True, exist_ok=True)

    original_counts = Counter()
    target_counts = Counter()
    image_class_counts = Counter()

    kept_images = 0
    excluded_images = 0
    mixed_class_images = 0
    removed_objects = 0

    excluded_filenames = []

    for stem, image_path in images.items():

        label_path = labels[stem]

        validate_image(image_path)

        result = process_label(
            label_path,
            class_mapping,
        )

        original_counts.update(
            result["original_counts"]
        )

        removed_objects += result["removed_objects"]

        processed_lines = result["lines"]

        if not processed_lines:
            excluded_images += 1
            excluded_filenames.append(image_path.name)
            continue

        kept_images += 1

        if result["removed_objects"] > 0:
            mixed_class_images += 1

        target_counts.update(
            result["target_counts"]
        )

        image_class_counts.update(
            result["target_counts"].keys()
        )

        shutil.copy2(
            image_path,
            output_images / image_path.name,
        )

        output_label = (
            output_labels / f"{stem}.txt"
        )

        output_label.write_text(
            "\n".join(processed_lines) + "\n",
            encoding="utf-8",
        )

    if kept_images == 0:
        raise ValueError(
            f"No target images retained: {image_directory}"
        )

    original_objects = sum(original_counts.values())
    retained_objects = sum(target_counts.values())

    assert len(images) == kept_images + excluded_images

    assert (
        original_objects
        == retained_objects + removed_objects
    )

    return {
        "original_images": len(images),
        "retained_images": kept_images,
        "excluded_images": excluded_images,
        "mixed_class_images": mixed_class_images,
        "original_objects": original_objects,
        "retained_objects": retained_objects,
        "removed_objects": removed_objects,
        "original_class_counts": dict(
            sorted(original_counts.items())
        ),
        "target_class_counts": {
            "Unripe": target_counts[0],
            "Ripe": target_counts[1],
        },
        "images_per_target_class": {
            "Unripe": image_class_counts[0],
            "Ripe": image_class_counts[1],
        },
        "excluded_filenames": excluded_filenames,
    }


def create_dataset_yaml(output_directory, names):
    """Create a YOLO-compatible dataset configuration."""

    config = {
        "train": "train/images",
        "val": "valid/images",
        "test": "test/images",
        "nc": len(names),
        "names": names,
    }

    yaml_path = output_directory / "data.yaml"

    with yaml_path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(
            config,
            file,
            sort_keys=False,
            allow_unicode=True,
        )


def aggregate_statistics(split_results):
    """Aggregate statistics across dataset splits."""

    numeric_fields = (
        "original_images",
        "retained_images",
        "excluded_images",
        "mixed_class_images",
        "original_objects",
        "retained_objects",
        "removed_objects",
    )

    totals = {
        field: sum(
            result[field]
            for result in split_results.values()
        )
        for field in numeric_fields
    }

    for field in (
        "original_class_counts",
        "target_class_counts",
        "images_per_target_class",
    ):
        counter = Counter()

        for result in split_results.values():
            counter.update(result[field])

        totals[field] = dict(counter)

    totals["image_retention_rate"] = round(
        totals["retained_images"]
        / totals["original_images"]
        * 100,
        2,
    )

    totals["object_retention_rate"] = round(
        totals["retained_objects"]
        / totals["original_objects"]
        * 100,
        2,
    )

    return totals


def print_summary(report):
    """Print preprocessing statistics."""

    print("\n" + "=" * 70)
    print(f"PREPROCESSING SUMMARY: {report['dataset'].upper()}")
    print("=" * 70)

    print(
        f"{'Split':<10}"
        f"{'Images':>10}"
        f"{'Retained':>10}"
        f"{'Excluded':>10}"
        f"{'Unripe':>10}"
        f"{'Ripe':>10}"
    )

    print("-" * 60)

    for split, result in report["splits"].items():

        counts = result["target_class_counts"]

        print(
            f"{split:<10}"
            f"{result['original_images']:>10}"
            f"{result['retained_images']:>10}"
            f"{result['excluded_images']:>10}"
            f"{counts['Unripe']:>10}"
            f"{counts['Ripe']:>10}"
        )

    totals = report["totals"]

    print("-" * 60)

    print(
        f"{'TOTAL':<10}"
        f"{totals['original_images']:>10}"
        f"{totals['retained_images']:>10}"
        f"{totals['excluded_images']:>10}"
        f"{totals['target_class_counts']['Unripe']:>10}"
        f"{totals['target_class_counts']['Ripe']:>10}"
    )

    print(
        f"\nOriginal objects: "
        f"{totals['original_objects']}"
    )

    print(
        f"Retained objects: "
        f"{totals['retained_objects']}"
    )

    print(
        f"Removed objects: "
        f"{totals['removed_objects']}"
    )

    print(
        f"Mixed-class images retained: "
        f"{totals['mixed_class_images']}"
    )

    print(
        f"Image retention rate: "
        f"{totals['image_retention_rate']}%"
    )

    print(
        f"Object retention rate: "
        f"{totals['object_retention_rate']}%"
    )

    print("=" * 70)


def preprocess_dataset(dataset_name, raw_root, layout):
    """Run the shared preprocessing pipeline."""

    config = load_config()

    if layout not in ("flat", "nested"):
        raise ValueError(
            f"Unsupported dataset layout: {layout}"
        )

    class_mapping = config["datasets"][
        dataset_name
    ]["class_mapping"]

    if not raw_root.is_dir():
        raise FileNotFoundError(
            f"Dataset not found: {raw_root}"
        )

    PROCESSED_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_root = PROCESSED_ROOT / dataset_name

    report_path = (
        REPORT_ROOT / f"{dataset_name}_summary.json"
    )

    if output_root.exists() or report_path.exists():
        raise FileExistsError(
            "Preprocessing output already exists. "
            "Back up or rename the previous output "
            "and report before running again."
        )

    split_results = {}

    print(f"\nDataset: {dataset_name}")
    print(f"Source: {raw_root}")
    print(f"Destination: {output_root}")

    # Build outputs in a temporary directory first.
    # Failed preprocessing will not leave a partial dataset.
    with TemporaryDirectory(
        prefix=f".{dataset_name}_",
        dir=PROCESSED_ROOT,
    ) as temporary_directory:

        temporary_root = (
            Path(temporary_directory) / dataset_name
        )

        temporary_root.mkdir()

        for split in SPLITS:

            print(f"\nProcessing {split} split...")

            if layout == "flat":
                image_directory = raw_root / split
                label_directory = raw_root / split

            else:
                image_directory = (
                    raw_root / split / "images"
                )

                label_directory = (
                    raw_root / split / "labels"
                )

            split_results[split] = process_split(
                image_directory=image_directory,
                label_directory=label_directory,
                output_directory=temporary_root / split,
                class_mapping=class_mapping,
            )

            print(
                f"Completed: "
                f"{split_results[split]['retained_images']} "
                "images retained."
            )

        create_dataset_yaml(
            temporary_root,
            config["names"],
        )

        report = {
            "dataset": dataset_name,
            "mapping_version": config["version"],
            "strategy": config["strategy"],
            "target_classes": config["names"],
            "source": raw_root.relative_to(
                PROJECT_ROOT
            ).as_posix(),
            "destination": output_root.relative_to(
                PROJECT_ROOT
            ).as_posix(),
            "validation_status": (
                "Preliminary preprocessing checks only. "
                "Duplicate and leakage checks are pending."
            ),
            "splits": split_results,
            "totals": aggregate_statistics(split_results),
        }

        temporary_report = (
            Path(temporary_directory) / "summary.json"
        )

        temporary_report.write_text(
            json.dumps(report, indent=4) + "\n",
            encoding="utf-8",
        )

        temporary_root.rename(output_root)

        try:
            shutil.move(
                str(temporary_report),
                str(report_path),
            )

        except Exception:
            output_root.rename(temporary_root)
            raise

    print_summary(report)

    print(f"\nProcessed dataset: {output_root}")
    print(f"Summary report: {report_path}")
    print("\nPreprocessing completed successfully.")

    return report
