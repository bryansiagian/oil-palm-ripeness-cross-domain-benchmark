
from .common import RAW_ROOT, preprocess_dataset


def main():
    preprocess_dataset(
        dataset_name="dataset2",
        raw_root=RAW_ROOT / "dataset2" / "yolov8",
        layout="nested",
    )


if __name__ == "__main__":
    main()
