
from pathlib import Path
from collections import Counter

# Root proyek, dihitung dari lokasi file script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = PROJECT_ROOT / "data" / "raw" / "dataset1"

total_images = 0
total_labels = 0
total_objects = 0
class_counts = Counter()

for split in ["train", "valid", "test"]:
    folder = DATASET_PATH / split

    if not folder.exists():
        print(f"ERROR: Folder tidak ditemukan: {folder}")
        continue

    images = list(folder.glob("*.jpg"))
    labels = list(folder.glob("*.txt"))

    split_counts = Counter()

    for label_file in labels:
        for line in label_file.read_text(encoding="utf-8").splitlines():
            parts = line.strip().split()

            if len(parts) != 5:
                if parts:
                    print(
                        f"WARNING: Format anotasi tidak sesuai "
                        f"di {label_file.name}: {line!r}"
                    )
                continue

            class_id = int(parts[0])
            split_counts[class_id] += 1

    image_count = len(images)
    label_count = len(labels)
    object_count = sum(split_counts.values())

    total_images += image_count
    total_labels += label_count
    total_objects += object_count
    class_counts.update(split_counts)

    print(f"\n=== {split.upper()} ===")
    print(f"Images       : {image_count}")
    print(f"Label files  : {label_count}")
    print(f"Objects      : {object_count}")
    print(f"Classes      : {dict(sorted(split_counts.items()))}")

print("\n=== DATASET SUMMARY ===")
print(f"Total images      : {total_images}")
print(f"Total label files : {total_labels}")
print(f"Total objects     : {total_objects}")

print("\nClass distribution:")
for class_id, count in sorted(class_counts.items()):
    print(f"Class {class_id}: {count} objects")
