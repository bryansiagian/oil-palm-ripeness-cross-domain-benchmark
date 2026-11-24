
from .common import RAW_ROOT, preprocess_dataset


def main():
    preprocess_dataset(
        dataset_name="dataset1",
        raw_root=RAW_ROOT / "dataset1",
        layout="flat",
    )


if __name__ == "__main__":
    main()
