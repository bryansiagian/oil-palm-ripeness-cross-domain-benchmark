
from pathlib import Path
from collections import Counter
from PIL import Image
import hashlib
import pandas as pd

# ==========================================
# CONFIGURATION
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    PROJECT_ROOT
    / "MunirahRosbi-Outdoor-Tenera-Oil-Palm-Fruit-Image-b27ea70"
)

AUDIT_PATH = DATASET_PATH / "audit_results"
AUDIT_PATH.mkdir(parents=True, exist_ok=True)

SPLITS = {
    "Train": DATASET_PATH / "FFBtrain",
    "Test": DATASET_PATH / "FFBtest",
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def calculate_sha256(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def get_class_name(folder_name):
    name = folder_name

    for prefix in ["Train", "Test"]:
        if name.startswith(prefix):
            name = name[len(prefix):]

    return name


# ==========================================
# MAIN AUDIT
# ==========================================

def main():

    records = []
    dimension_counts = Counter()

    total_images = 0
    valid_images = 0
    corrupted_images = 0

    print("=" * 55)
    print("DATASET 3 - IMAGE AUDIT")
    print("=" * 55)

    for split, split_path in SPLITS.items():

        if not split_path.exists():
            print(f"ERROR: Folder not found: {split_path}")
            continue

        split_counts = Counter()

        for class_folder in sorted(split_path.iterdir()):

            if not class_folder.is_dir():
                continue

            class_name = get_class_name(class_folder.name)

            images = sorted(
                path for path in class_folder.rglob("*")
                if path.is_file()
                and path.suffix.lower() in IMAGE_EXTENSIONS
            )

            for image_path in images:

                total_images += 1

                try:
                    with Image.open(image_path) as image:
                        image.verify()

                    with Image.open(image_path) as image:
                        image_format = image.format
                        color_mode = image.mode
                        width, height = image.size

                    valid_images += 1
                    split_counts[class_name] += 1
                    dimension_counts[(width, height)] += 1

                    records.append({
                        "File": str(image_path.relative_to(DATASET_PATH)),
                        "Split": split,
                        "Class": class_name,
                        "Format": image_format,
                        "Mode": color_mode,
                        "Width": width,
                        "Height": height,
                        "SHA256": calculate_sha256(image_path),
                    })

                except Exception as error:

                    corrupted_images += 1

                    print(
                        f"CORRUPTED: {image_path.name} "
                        f"| {error}"
                    )

        print(f"\n=== {split.upper()} ===")

        for class_name, count in sorted(split_counts.items()):
            print(f"{class_name:<15}: {count}")

        print(f"Total {split} images: {sum(split_counts.values())}")

    # ======================================
    # IMAGE SUMMARY
    # ======================================

    df = pd.DataFrame(records)

    print("\n=== IMAGE INTEGRITY SUMMARY ===")
    print(f"Total images     : {total_images}")
    print(f"Valid images     : {valid_images}")
    print(f"Corrupted images : {corrupted_images}")

    if not df.empty:

        print("\nImage formats:")
        print(df["Format"].value_counts().to_string())

        print("\nColor modes:")
        print(df["Mode"].value_counts().to_string())

        print("\n=== ORIGINAL CLASS DISTRIBUTION ===")

        distribution = pd.crosstab(
            df["Split"],
            df["Class"]
        )

        print(distribution.to_string())

        print("\n=== IMAGE DIMENSIONS ===")

        for dimension, count in dimension_counts.most_common():
            print(f"{dimension[0]}x{dimension[1]}: {count}")

        # ==================================
        # SAVE HASH REPORT
        # ==================================

        hash_path = AUDIT_PATH / "dataset3_sha256_hashes.csv"
        df.to_csv(hash_path, index=False)

        # ==================================
        # DUPLICATE DETECTION
        # ==================================

        duplicate_rows = []

        for sha, group in df.groupby("SHA256"):

            if len(group) > 1:

                for _, row in group.iterrows():

                    duplicate_rows.append({
                        "SHA256": sha,
                        "File": row["File"],
                        "Split": row["Split"],
                        "Class": row["Class"],
                    })

        duplicates = pd.DataFrame(duplicate_rows)

        duplicate_path = AUDIT_PATH / "dataset3_duplicates.csv"
        duplicates.to_csv(duplicate_path, index=False)

        # ==================================
        # CROSS-SPLIT AND SAME-SPLIT
        # ==================================

        cross_groups = []
        same_groups = []

        for sha, group in df.groupby("SHA256"):

            if len(group) <= 1:
                continue

            splits = set(group["Split"])

            if len(splits) > 1:
                cross_groups.append(group)
            else:
                same_groups.append(group)

        cross_df = (
            pd.concat(cross_groups, ignore_index=True)
            if cross_groups else pd.DataFrame(columns=df.columns)
        )

        same_df = (
            pd.concat(same_groups, ignore_index=True)
            if same_groups else pd.DataFrame(columns=df.columns)
        )

        cross_df.to_csv(
            AUDIT_PATH / "dataset3_cross_split_duplicates.csv",
            index=False
        )

        same_df.to_csv(
            AUDIT_PATH / "dataset3_same_split_duplicates.csv",
            index=False
        )

        # ==================================
        # PROPOSED EXCLUSION MANIFEST
        # ==================================

        exclusions = []

        for sha, group in df.groupby("SHA256"):

            if len(group) <= 1:
                continue

            splits = set(group["Split"])

            if len(splits) > 1:

                # Keep Test, exclude identical Train copies.
                excluded = group[group["Split"] == "Train"]

                reason = "Cross-split duplicate"

            else:

                # Keep one representative file.
                ordered = group.sort_values("File")
                excluded = ordered.iloc[1:]

                reason = "Same-split duplicate"

            for _, row in excluded.iterrows():

                exclusions.append({
                    "SHA256": sha,
                    "File": row["File"],
                    "Split": row["Split"],
                    "Class": row["Class"],
                    "Reason": reason,
                })

        exclusion_df = pd.DataFrame(exclusions)

        exclusion_df.to_csv(
            AUDIT_PATH / "dataset3_combined_exclusion_manifest.csv",
            index=False
        )

        # ==================================
        # FINAL SUMMARY
        # ==================================

        excluded_files = set(exclusion_df["File"]) if not exclusion_df.empty else set()

        remaining = df[~df["File"].isin(excluded_files)]

        print("\n=== DUPLICATE AUDIT SUMMARY ===")
        print(f"Total images hashed       : {len(df)}")
        print(f"Unique SHA256 hashes      : {df['SHA256'].nunique()}")
        print(f"Duplicate hash groups     : {df['SHA256'].duplicated(keep=False).sum() and len(duplicates['SHA256'].unique())}")
        print(f"Cross-split duplicate groups: {cross_df['SHA256'].nunique()}")
        print(f"Same-split duplicate groups : {same_df['SHA256'].nunique()}")
        print(f"Recommended exclusions   : {len(exclusion_df)}")
        print(f"Remaining images         : {len(remaining)}")
        print(f"Remaining unique hashes  : {remaining['SHA256'].nunique()}")

        print("\n=== DISTRIBUTION AFTER PROPOSED EXCLUSIONS ===")

        print(
            pd.crosstab(
                remaining["Split"],
                remaining["Class"]
            ).to_string()
        )

        print("\nAudit output directory:")
        print(AUDIT_PATH)

    # ======================================
    # ANNOTATION FILE INSPECTION
    # ======================================

    annotation_extensions = {
        ".txt", ".xml", ".json", ".csv", ".yaml", ".yml"
    }

    annotation_files = [
        path for path in DATASET_PATH.rglob("*")
        if path.is_file()
        and path.suffix.lower() in annotation_extensions
        and AUDIT_PATH not in path.parents
    ]

    print("\n=== ANNOTATION FILE INSPECTION ===")
    print(f"Possible annotation/metadata files: {len(annotation_files)}")

    for path in annotation_files:
        print(path.relative_to(DATASET_PATH))


if __name__ == "__main__":
    main()
