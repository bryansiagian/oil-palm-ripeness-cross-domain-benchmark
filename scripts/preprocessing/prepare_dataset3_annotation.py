
from pathlib import Path
from collections import Counter
from tempfile import TemporaryDirectory
import hashlib
import json
import shutil

import pandas as pd
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_ROOT = PROJECT_ROOT / "data" / "raw" / "dataset3"

AUDIT_ROOT = RAW_ROOT / "audit_results"

ANNOTATION_ROOT = (
    PROJECT_ROOT
    / "data"
    / "annotation"
    / "dataset3"
)

REPORT_ROOT = (
    PROJECT_ROOT
    / "results"
    / "preprocessing"
)

CONFIG_PATH = (
    PROJECT_ROOT
    / "configs"
    / "class_mapping.yaml"
)

HASH_REPORT = (
    AUDIT_ROOT
    / "dataset3_sha256_hashes.csv"
)

EXCLUSION_REPORT = (
    AUDIT_ROOT
    / "dataset3_combined_exclusion_manifest.csv"
)

AUDIT_SUMMARY = (
    AUDIT_ROOT
    / "dataset3_audit_summary.json"
)

REPORT_PATH = (
    REPORT_ROOT
    / "dataset3_annotation_preparation_summary.json"
)

SPLITS = ("train", "test")


def calculate_sha256(file_path):
    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024), b""
        ):
            sha256.update(chunk)

    return sha256.hexdigest()


def load_class_mapping():
    with CONFIG_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        config = yaml.safe_load(file)

    names = config["names"]

    if names != {0: "Unripe", 1: "Ripe"}:
        raise ValueError(
            "Unexpected target class taxonomy."
        )

    mapping = config["datasets"]["dataset3"][
        "class_mapping"
    ]

    if mapping.get("Unripe") != 0:
        raise ValueError(
            "Unripe must map to class ID 0."
        )

    if mapping.get("Ripe") != 1:
        raise ValueError(
            "Ripe must map to class ID 1."
        )

    target_mapping = {
        name: class_id
        for name, class_id in mapping.items()
        if class_id is not None
    }

    if target_mapping != {
        "Unripe": 0,
        "Ripe": 1,
    }:
        raise ValueError(
            "Unexpected Dataset 3 class mapping."
        )

    return names, target_mapping


def load_audit_reports():
    required_files = [
        HASH_REPORT,
        EXCLUSION_REPORT,
        AUDIT_SUMMARY,
    ]

    for path in required_files:
        if not path.is_file():
            raise FileNotFoundError(
                f"Missing audit report: {path}"
            )

    with AUDIT_SUMMARY.open(
        "r",
        encoding="utf-8",
    ) as file:
        summary = json.load(file)

    if summary["audit_status"] != "Completed":
        raise RuntimeError(
            "Dataset audit requires manual review."
        )

    if summary["corrupted_images"] != 0:
        raise RuntimeError(
            "Corrupted images detected."
        )

    if summary[
        "conflicting_class_duplicate_groups"
    ] != 0:
        raise RuntimeError(
            "Conflicting class duplicates detected."
        )

    records = pd.read_csv(HASH_REPORT)

    exclusions = pd.read_csv(EXCLUSION_REPORT)

    required_columns = {
        "File",
        "Split",
        "Class",
        "SHA256",
    }

    if not required_columns.issubset(
        records.columns
    ):
        raise ValueError(
            "Invalid hash report structure."
        )

    if not required_columns.issubset(
        exclusions.columns
    ):
        raise ValueError(
            "Invalid exclusion report structure."
        )

    if records["File"].duplicated().any():
        raise ValueError(
            "Duplicate paths in hash report."
        )

    if exclusions["File"].duplicated().any():
        raise ValueError(
            "Duplicate paths in exclusion report."
        )

    if len(records) != summary["valid_images"]:
        raise ValueError(
            "Hash report and audit summary mismatch."
        )

    if len(exclusions) != summary[
        "recommended_exclusions"
    ]:
        raise ValueError(
            "Exclusion report and audit summary mismatch."
        )

    if not set(exclusions["File"]).issubset(
        set(records["File"])
    ):
        raise ValueError(
            "Unknown files in exclusion report."
        )

    return records, exclusions, summary


def filter_records(
    records,
    exclusions,
    summary,
    target_mapping,
):
    excluded_files = set(exclusions["File"])

    remaining = records[
        ~records["File"].isin(excluded_files)
    ].copy()

    if remaining["SHA256"].duplicated().any():
        raise RuntimeError(
            "Duplicate hashes remain after filtering."
        )

    if len(remaining) != summary["remaining_images"]:
        raise ValueError(
            "Unexpected remaining image count."
        )

    targets = remaining[
        remaining["Class"].isin(target_mapping)
    ].copy()

    if len(targets) != summary[
        "target_images_after_proposed_exclusions"
    ]:
        raise ValueError(
            "Unexpected target image count."
        )

    targets = targets.sort_values(
        ["Split", "Class", "File"]
    )

    return remaining, targets


def resolve_source(relative_path):
    source = (RAW_ROOT / relative_path).resolve()

    if not source.is_relative_to(
        RAW_ROOT.resolve()
    ):
        raise ValueError(
            f"Invalid source path: {relative_path}"
        )

    if not source.is_file():
        raise FileNotFoundError(
            f"Source image not found: {source}"
        )

    return source


def verify_source_records(records):
    print("\nVerifying original image hashes...")

    for _, row in records.iterrows():
        source = resolve_source(row["File"])

        actual_hash = calculate_sha256(source)

        if actual_hash != row["SHA256"]:
            raise RuntimeError(
                f"Image changed after audit: {source}"
            )

    print(
        f"Verified {len(records)} original images."
    )


def prepare_directories(output_root):
    for split in SPLITS:
        (output_root / split / "images").mkdir(
            parents=True,
            exist_ok=True,
        )

        (output_root / split / "labels").mkdir(
            parents=True,
            exist_ok=True,
        )


def copy_target_images(
    targets,
    output_root,
    target_mapping,
):
    manifest = []

    split_counters = {
        split: 0
        for split in SPLITS
    }

    for _, row in targets.iterrows():
        split = row["Split"].lower()
        class_name = row["Class"]
        class_id = target_mapping[class_name]

        if split not in SPLITS:
            raise ValueError(
                f"Unexpected split: {split}"
            )

        source = resolve_source(row["File"])

        split_counters[split] += 1

        index = split_counters[split]

        filename = (
            f"d3_{split}_{index:04d}"
            f"{source.suffix.lower()}"
        )

        destination = (
            output_root
            / split
            / "images"
            / filename
        )

        if destination.exists():
            raise FileExistsError(
                f"Duplicate destination: {destination}"
            )

        shutil.copy2(source, destination)

        copied_hash = calculate_sha256(destination)

        if copied_hash != row["SHA256"]:
            raise RuntimeError(
                f"Copied image hash mismatch: {destination}"
            )

        manifest.append({
            "source_file": row["File"],
            "annotation_image": (
                destination.relative_to(
                    output_root
                ).as_posix()
            ),
            "expected_label": (
                f"{split}/labels/"
                f"{destination.stem}.txt"
            ),
            "split": split,
            "source_class": class_name,
            "source_class_id": class_id,
            "sha256": row["SHA256"],
            "annotation_status": "pending",
        })

    return pd.DataFrame(manifest)


def save_annotation_files(
    output_root,
    manifest,
    names,
):
    classes_path = output_root / "classes.txt"

    classes_path.write_text(
        "\n".join(
            names[class_id]
            for class_id in sorted(names)
        ) + "\n",
        encoding="utf-8",
    )

    manifest.to_csv(
        output_root / "annotation_manifest.csv",
        index=False,
    )


def build_summary(
    records,
    exclusions,
    remaining,
    targets,
    manifest,
):
    distribution = {}

    for split in SPLITS:
        subset = manifest[
            manifest["split"] == split
        ]

        counts = Counter(
            subset["source_class"]
        )

        distribution[split] = {
            "images": len(subset),
            "Unripe": counts.get("Unripe", 0),
            "Ripe": counts.get("Ripe", 0),
        }

    counts = Counter(
        manifest["source_class"]
    )

    distribution["total"] = {
        "images": len(manifest),
        "Unripe": counts.get("Unripe", 0),
        "Ripe": counts.get("Ripe", 0),
    }

    return {
        "dataset": "dataset3",
        "source": RAW_ROOT.relative_to(
            PROJECT_ROOT
        ).as_posix(),
        "destination": ANNOTATION_ROOT.relative_to(
            PROJECT_ROOT
        ).as_posix(),
        "original_images": len(records),
        "duplicate_exclusions": len(exclusions),
        "unique_images": len(remaining),
        "non_target_exclusions": (
            len(remaining) - len(targets)
        ),
        "prepared_images": len(manifest),
        "target_classes": {
            0: "Unripe",
            1: "Ripe",
        },
        "distribution": distribution,
        "remaining_duplicate_images": int(
            manifest["sha256"].duplicated().sum()
        ),
        "original_test_split_preserved": True,
        "raw_data_modified": False,
        "bounding_box_annotations_created": 0,
        "annotation_status": "Pending",
        "preparation_status": "Completed",
    }


def validate_manifest(manifest, summary):
    if manifest["sha256"].duplicated().any():
        raise RuntimeError(
            "Duplicate images in annotation workspace."
        )

    if manifest["annotation_image"].duplicated().any():
        raise RuntimeError(
            "Duplicate annotation image paths."
        )

    for split in SPLITS:
        expected = summary[
            "target_split_distribution"
        ][split.capitalize()]

        subset = manifest[
            manifest["split"] == split
        ]

        for class_name in ("Unripe", "Ripe"):
            actual = int(
                (
                    subset["source_class"]
                    == class_name
                ).sum()
            )

            if actual != expected[class_name]:
                raise ValueError(
                    f"Distribution mismatch: "
                    f"{split} / {class_name}"
                )


def print_summary(summary):
    print("\n=== ANNOTATION PREPARATION SUMMARY ===")

    print(
        f"Original images      : "
        f"{summary['original_images']}"
    )

    print(
        f"Duplicate exclusions : "
        f"{summary['duplicate_exclusions']}"
    )

    print(
        f"Unique images        : "
        f"{summary['unique_images']}"
    )

    print(
        f"Non-target exclusions: "
        f"{summary['non_target_exclusions']}"
    )

    print(
        f"Prepared images      : "
        f"{summary['prepared_images']}"
    )

    print(
        f"Remaining duplicates : "
        f"{summary['remaining_duplicate_images']}"
    )

    print("\n=== TARGET DISTRIBUTION ===")

    print(
        f"{'Split':<12}"
        f"{'Images':>10}"
        f"{'Unripe':>10}"
        f"{'Ripe':>10}"
    )

    for split, values in (
        summary["distribution"].items()
    ):
        print(
            f"{split:<12}"
            f"{values['images']:>10}"
            f"{values['Unripe']:>10}"
            f"{values['Ripe']:>10}"
        )

    print("\n=== FINAL STATUS ===")
    print("Preparation: Completed")
    print("Bounding box annotation: Pending")
    print("Raw dataset files remain unchanged.")
    print(f"Annotation directory: {ANNOTATION_ROOT}")
    print(f"Summary report: {REPORT_PATH}")


def main():
    print("=" * 60)
    print("DATASET 3 - ANNOTATION PREPARATION")
    print("=" * 60)

    if ANNOTATION_ROOT.exists():
        raise FileExistsError(
            f"Annotation workspace already exists: "
            f"{ANNOTATION_ROOT}. "
            "Back it up before running again."
        )

    if REPORT_PATH.exists():
        raise FileExistsError(
            f"Preparation report already exists: "
            f"{REPORT_PATH}"
        )

    names, target_mapping = load_class_mapping()

    records, exclusions, audit_summary = (
        load_audit_reports()
    )

    verify_source_records(records)

    remaining, targets = filter_records(
        records,
        exclusions,
        audit_summary,
        target_mapping,
    )

    ANNOTATION_ROOT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    with TemporaryDirectory(
        dir=ANNOTATION_ROOT.parent
    ) as temporary_directory:
        temporary_root = Path(
            temporary_directory
        )

        output_root = (
            temporary_root / "dataset3"
        )

        prepare_directories(output_root)

        manifest = copy_target_images(
            targets,
            output_root,
            target_mapping,
        )

        validate_manifest(
            manifest,
            audit_summary,
        )

        save_annotation_files(
            output_root,
            manifest,
            names,
        )

        summary = build_summary(
            records,
            exclusions,
            remaining,
            targets,
            manifest,
        )

        temporary_report = (
            temporary_root / "summary.json"
        )

        with temporary_report.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                summary,
                file,
                indent=4,
                ensure_ascii=False,
            )

        output_root.rename(ANNOTATION_ROOT)

        try:
            shutil.move(
                str(temporary_report),
                str(REPORT_PATH),
            )

        except Exception:
            shutil.rmtree(ANNOTATION_ROOT)
            raise

    print_summary(summary)


if __name__ == "__main__":
    main()
