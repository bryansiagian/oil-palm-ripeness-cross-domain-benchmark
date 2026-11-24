
from pathlib import Path
from collections import Counter
from PIL import Image
import hashlib
import json
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = PROJECT_ROOT / "data" / "raw" / "dataset3"
AUDIT_PATH = DATASET_PATH / "audit_results"

SPLITS = {
    "Train": DATASET_PATH / "FFBtrain",
    "Test": DATASET_PATH / "FFBtest",
}

EXPECTED_CLASSES = {
    "Damaged",
    "Empty",
    "Overripe",
    "Ripe",
    "Unripe",
}

TARGET_CLASSES = {"Unripe", "Ripe"}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

ANNOTATION_EXTENSIONS = {
    ".txt", ".xml", ".json", ".csv", ".yaml", ".yml"
}

RECORD_COLUMNS = [
    "File",
    "Split",
    "Class",
    "Format",
    "Mode",
    "Width",
    "Height",
    "SHA256",
]

EXCLUSION_COLUMNS = [
    "SHA256",
    "File",
    "Split",
    "Class",
    "Reason",
    "RetainedFile",
]


def calculate_sha256(file_path):
    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024), b""
        ):
            sha256.update(chunk)

    return sha256.hexdigest()


def get_class_name(folder_name):
    for prefix in ("Train", "Test"):
        if folder_name.startswith(prefix):
            return folder_name[len(prefix):]

    return folder_name


def validate_directory_structure():
    if not DATASET_PATH.is_dir():
        raise FileNotFoundError(
            f"Dataset directory not found: {DATASET_PATH}"
        )

    for split, split_path in SPLITS.items():
        if not split_path.is_dir():
            raise FileNotFoundError(
                f"Missing split directory: {split_path}"
            )

        actual_folders = {
            path.name
            for path in split_path.iterdir()
            if path.is_dir()
        }

        expected_folders = {
            f"{split}{class_name}"
            for class_name in EXPECTED_CLASSES
        }

        missing = expected_folders - actual_folders
        unexpected = actual_folders - expected_folders

        if missing:
            raise ValueError(
                f"Missing class folders in {split}: "
                f"{sorted(missing)}"
            )

        if unexpected:
            raise ValueError(
                f"Unexpected class folders in {split}: "
                f"{sorted(unexpected)}"
            )


def inspect_image(image_path, split, class_name):
    with Image.open(image_path) as image:
        image.verify()

    with Image.open(image_path) as image:
        image.load()

        image_format = image.format
        color_mode = image.mode
        width, height = image.size

        if width <= 0 or height <= 0:
            raise ValueError("Invalid image dimensions")

    return {
        "File": image_path.relative_to(
            DATASET_PATH
        ).as_posix(),
        "Split": split,
        "Class": class_name,
        "Format": image_format,
        "Mode": color_mode,
        "Width": width,
        "Height": height,
        "SHA256": calculate_sha256(image_path),
    }


def collect_image_records():
    records = []
    corrupted = []
    dimension_counts = Counter()
    total_images = 0

    for split, split_path in SPLITS.items():
        split_counts = Counter()

        for class_folder in sorted(split_path.iterdir()):
            if not class_folder.is_dir():
                continue

            class_name = get_class_name(
                class_folder.name
            )

            images = sorted(
                path
                for path in class_folder.rglob("*")
                if path.is_file()
                and path.suffix.lower() in IMAGE_EXTENSIONS
            )

            if not images:
                raise ValueError(
                    f"No images found in {class_folder}"
                )

            for image_path in images:
                total_images += 1

                try:
                    record = inspect_image(
                        image_path,
                        split,
                        class_name,
                    )

                    records.append(record)

                    split_counts[class_name] += 1

                    dimension_counts[
                        (record["Width"], record["Height"])
                    ] += 1

                except Exception as error:
                    corrupted.append({
                        "File": image_path.relative_to(
                            DATASET_PATH
                        ).as_posix(),
                        "Split": split,
                        "Class": class_name,
                        "Error": str(error),
                    })

                    print(
                        f"CORRUPTED: {image_path.name}"
                        f" | {error}"
                    )

        print(f"\n=== {split.upper()} ===")

        for class_name, count in sorted(
            split_counts.items()
        ):
            print(f"{class_name:<15}: {count}")

        print(
            f"Total valid {split} images: "
            f"{sum(split_counts.values())}"
        )

    return (
        pd.DataFrame(records, columns=RECORD_COLUMNS),
        corrupted,
        dimension_counts,
        total_images,
    )


def analyze_duplicates(df):
    duplicate_groups = []
    cross_groups = []
    same_groups = []
    conflict_groups = []
    exclusions = []

    for sha, group in df.groupby("SHA256"):
        if len(group) <= 1:
            continue

        duplicate_groups.append(group)

        splits = set(group["Split"])
        classes = set(group["Class"])

        if len(splits) > 1:
            cross_groups.append(group)
        else:
            same_groups.append(group)

        # Conflicting class labels require manual review.
        if len(classes) > 1:
            conflict_groups.append(group)
            continue

        # Prefer the original test split.
        ordered = group.assign(
            Priority=group["Split"].map({
                "Test": 0,
                "Train": 1,
            })
        ).sort_values(["Priority", "File"])

        retained = ordered.iloc[0]

        for _, row in ordered.iloc[1:].iterrows():
            if row["Split"] != retained["Split"]:
                reason = "Cross-split duplicate"
            else:
                reason = "Same-split duplicate"

            exclusions.append({
                "SHA256": sha,
                "File": row["File"],
                "Split": row["Split"],
                "Class": row["Class"],
                "Reason": reason,
                "RetainedFile": retained["File"],
            })

    def combine_groups(groups):
        if groups:
            return pd.concat(
                groups,
                ignore_index=True,
            )

        return pd.DataFrame(columns=RECORD_COLUMNS)

    return {
        "duplicates": combine_groups(duplicate_groups),
        "cross_split": combine_groups(cross_groups),
        "same_split": combine_groups(same_groups),
        "conflicts": combine_groups(conflict_groups),
        "exclusions": pd.DataFrame(
            exclusions,
            columns=EXCLUSION_COLUMNS,
        ),
    }


def inspect_annotation_files():
    return sorted(
        path.relative_to(DATASET_PATH).as_posix()
        for path in DATASET_PATH.rglob("*")
        if path.is_file()
        and path.suffix.lower() in ANNOTATION_EXTENSIONS
        and AUDIT_PATH not in path.parents
    )


def build_distribution(df):
    distribution = {}

    for split in SPLITS:
        subset = df[df["Split"] == split]

        distribution[split] = {
            class_name: int(
                (subset["Class"] == class_name).sum()
            )
            for class_name in sorted(EXPECTED_CLASSES)
        }

        distribution[split]["Total"] = len(subset)

    distribution["Total"] = {
        class_name: int(
            (df["Class"] == class_name).sum()
        )
        for class_name in sorted(EXPECTED_CLASSES)
    }

    distribution["Total"]["Total"] = len(df)

    return distribution


def save_csv_reports(df, corrupted, analysis):
    AUDIT_PATH.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        AUDIT_PATH / "dataset3_sha256_hashes.csv",
        index=False,
    )

    pd.DataFrame(
        corrupted,
        columns=["File", "Split", "Class", "Error"],
    ).to_csv(
        AUDIT_PATH / "dataset3_corrupted_images.csv",
        index=False,
    )

    reports = {
        "duplicates": "dataset3_duplicates.csv",
        "cross_split": (
            "dataset3_cross_split_duplicates.csv"
        ),
        "same_split": (
            "dataset3_same_split_duplicates.csv"
        ),
        "conflicts": (
            "dataset3_conflicting_class_duplicates.csv"
        ),
        "exclusions": (
            "dataset3_combined_exclusion_manifest.csv"
        ),
    }

    for key, filename in reports.items():
        analysis[key].to_csv(
            AUDIT_PATH / filename,
            index=False,
        )


def main():
    print("=" * 60)
    print("DATASET 3 - IMAGE AUDIT")
    print("=" * 60)

    print(f"Dataset directory: {DATASET_PATH}")

    validate_directory_structure()

    (
        df,
        corrupted,
        dimension_counts,
        total_images,
    ) = collect_image_records()

    if df.empty:
        raise RuntimeError("No valid images found.")

    analysis = analyze_duplicates(df)

    excluded_files = set(
        analysis["exclusions"]["File"]
    )

    remaining = df[
        ~df["File"].isin(excluded_files)
    ].copy()

    target_images = remaining[
        remaining["Class"].isin(TARGET_CLASSES)
    ].copy()

    annotation_files = inspect_annotation_files()

    save_csv_reports(
        df,
        corrupted,
        analysis,
    )

    conflict_count = int(
        analysis["conflicts"]["SHA256"].nunique()
    )

    remaining_duplicates = (
        len(remaining)
        - remaining["SHA256"].nunique()
    )

    summary = {
        "dataset": "dataset3",
        "source": DATASET_PATH.relative_to(
            PROJECT_ROOT
        ).as_posix(),
        "annotation_format": "image_classification",
        "total_images": total_images,
        "valid_images": len(df),
        "corrupted_images": len(corrupted),
        "unique_sha256_hashes": int(
            df["SHA256"].nunique()
        ),
        "duplicate_hash_groups": int(
            analysis["duplicates"]["SHA256"].nunique()
        ),
        "cross_split_duplicate_groups": int(
            analysis["cross_split"]["SHA256"].nunique()
        ),
        "same_split_duplicate_groups": int(
            analysis["same_split"]["SHA256"].nunique()
        ),
        "conflicting_class_duplicate_groups": (
            conflict_count
        ),
        "recommended_exclusions": len(excluded_files),
        "cross_split_exclusions": int(
            (
                analysis["exclusions"]["Reason"]
                == "Cross-split duplicate"
            ).sum()
        ),
        "same_split_exclusions": int(
            (
                analysis["exclusions"]["Reason"]
                == "Same-split duplicate"
            ).sum()
        ),
        "remaining_images": len(remaining),
        "remaining_unique_hashes": int(
            remaining["SHA256"].nunique()
        ),
        "remaining_duplicate_images": int(
            remaining_duplicates
        ),
        "target_images_after_proposed_exclusions": (
            len(target_images)
        ),
        "target_class_distribution": {
            class_name: int(
                (target_images["Class"] == class_name).sum()
            )
            for class_name in sorted(TARGET_CLASSES)
        },
        "target_split_distribution": {
            split: {
                class_name: int(
                    (
                        (target_images["Split"] == split)
                        & (
                            target_images["Class"]
                            == class_name
                        )
                    ).sum()
                )
                for class_name in sorted(TARGET_CLASSES)
            }
            for split in SPLITS
        },
        "original_distribution": build_distribution(df),
        "distribution_after_proposed_exclusions": (
            build_distribution(remaining)
        ),
        "image_formats": {
            str(key): int(value)
            for key, value in (
                df["Format"].value_counts().items()
            )
        },
        "color_modes": {
            str(key): int(value)
            for key, value in (
                df["Mode"].value_counts().items()
            )
        },
        "image_dimensions": {
            f"{width}x{height}": count
            for (width, height), count
            in dimension_counts.most_common()
        },
        "possible_annotation_files": annotation_files,
        "bounding_box_annotation_status": "Pending",
        "exclusions_applied_to_raw_data": False,
        "audit_status": (
            "Manual review required"
            if conflict_count or corrupted
            or remaining_duplicates
            else "Completed"
        ),
    }

    summary_path = AUDIT_PATH / "dataset3_audit_summary.json"

    with summary_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            indent=4,
            ensure_ascii=False,
        )

    print("\n=== IMAGE INTEGRITY SUMMARY ===")
    print(f"Total images     : {total_images}")
    print(f"Valid images     : {len(df)}")
    print(f"Corrupted images : {len(corrupted)}")

    print("\n=== IMAGE FORMATS ===")
    print(df["Format"].value_counts().to_string())

    print("\n=== COLOR MODES ===")
    print(df["Mode"].value_counts().to_string())

    print("\n=== ORIGINAL CLASS DISTRIBUTION ===")
    print(
        pd.crosstab(
            df["Split"],
            df["Class"],
            margins=True,
        ).to_string()
    )

    print("\n=== IMAGE DIMENSIONS ===")

    for dimension, count in (
        dimension_counts.most_common()
    ):
        print(
            f"{dimension[0]}x{dimension[1]}: {count}"
        )

    print("\n=== DUPLICATE AUDIT SUMMARY ===")

    fields = [
        "unique_sha256_hashes",
        "duplicate_hash_groups",
        "cross_split_duplicate_groups",
        "same_split_duplicate_groups",
        "conflicting_class_duplicate_groups",
        "recommended_exclusions",
        "cross_split_exclusions",
        "same_split_exclusions",
        "remaining_images",
        "remaining_unique_hashes",
        "remaining_duplicate_images",
    ]

    for field in fields:
        print(
            f"{field.replace('_', ' ').capitalize():<40}"
            f": {summary[field]}"
        )

    print(
        "\n=== DISTRIBUTION AFTER "
        "PROPOSED EXCLUSIONS ==="
    )

    print(
        pd.crosstab(
            remaining["Split"],
            remaining["Class"],
            margins=True,
        ).to_string()
    )

    print("\n=== TARGET CLASS DISTRIBUTION ===")

    print(
        pd.crosstab(
            target_images["Split"],
            target_images["Class"],
            margins=True,
        ).to_string()
    )

    print(f"\nTotal target images: {len(target_images)}")

    print("\n=== ANNOTATION FILE INSPECTION ===")

    print(
        "Possible annotation/metadata files: "
        f"{len(annotation_files)}"
    )

    for path in annotation_files:
        print(path)

    print("\n=== FINAL AUDIT STATUS ===")
    print(f"Status: {summary['audit_status']}")
    print("Raw dataset files remain unchanged.")
    print(f"Audit output directory: {AUDIT_PATH}")
    print(f"Summary report: {summary_path}")

    if summary["audit_status"] != "Completed":
        raise SystemExit(
            "Audit requires manual review before "
            "dataset preparation can continue."
        )


if __name__ == "__main__":
    main()
