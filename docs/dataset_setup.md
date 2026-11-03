# Dataset Setup Guide

This repository does **not** redistribute the original datasets. Download each dataset from its official source and store it locally under `data/raw/`.

## 1. Directory structure

From the repository root, create the following structure:

```text
oil-palm-ripeness-cross-domain-benchmark/
├── data/
│   └── raw/
│       └── dataset1/
│           ├── train/
│           │   ├── <image-name>.jpg
│           │   └── <image-name>.txt
│           ├── valid/
│           │   ├── <image-name>.jpg
│           │   └── <image-name>.txt
│           └── test/
│               ├── <image-name>.jpg
│               └── <image-name>.txt
├── docs/
│   └── dataset_setup.md
├── scripts/
│   └── audit_dataset1.py
├── .gitignore
└── README.md
```

The image and matching `.txt` annotation files are stored together. Each annotation line follows the YOLO detection format:

```text
<class_id> <x_center> <y_center> <width> <height>
```

Bounding-box coordinates are normalized to the range 0–1. **Class ID to class name mapping has not yet been verified.** Do not assume the numerical ID order.

## 2. Dataset 1 — South Kalimantan palm oil mill (2023)

**Publication:** [Annotated Datasets of Oil Palm Fruit Bunch Piles for Ripeness Grading Using Deep Learning](https://www.nature.com/articles/s41597-023-01958-x)

**Data repository:** [Science Data Bank](https://doi.org/10.57760/sciencedb.j00001.00713)

Download these three archives from the data repository:

- `train_rev2.zip`
- `valid_rev2.zip`
- `test_rev2.zip`

Extract each archive. Copy the **inner** `train`, `valid`, and `test` directories into `data/raw/dataset1/`. Do not nest the outer `train_rev2`, `valid_rev2`, or `test_rev2` directories there.

Expected paths include:

```text
data/raw/dataset1/train/<image-name>.jpg
data/raw/dataset1/train/<image-name>.txt
data/raw/dataset1/valid/<image-name>.jpg
data/raw/dataset1/valid/<image-name>.txt
data/raw/dataset1/test/<image-name>.jpg
data/raw/dataset1/test/<image-name>.txt
```

### Initial audit results

| Split | Images | Label files | Counted objects |
|---|---:|---:|---:|
| Train | 2,908 | 2,908 | 10,140 |
| Validation | 835 | 835 | 3,008 |
| Test | 417 | 417 | 1,410 |
| **Total** | **4,160** | **4,160** | **14,558** |

The article reports 14,559 objects, whereas the initial audit script counts 14,558. This one-object discrepancy is **unresolved**. The script counts nonempty lines with exactly five fields; additional image and bounding-box integrity checks are pending.

To reproduce the initial audit from the repository root:

```bash
python scripts/audit_dataset1.py
```

The command requires the audit script to be present in the repository.

## 3. Datasets 2 and 3 — pending audit

- **Dataset 2:** [Central Kalimantan plantation (Scientific Data, 2025)](https://doi.org/10.1038/s41597-025-05227-x)
- **Dataset 3:** [Malaysia outdoor oil palm (Zenodo)](https://zenodo.org/records/11114885)

Their extraction layout, annotation format, and class mapping will be documented after inspection. **Do not assume** that either dataset uses the same directory structure or class IDs as Dataset 1.

## 4. Git tracking

Keep raw datasets out of version control. Ensure `.gitignore` contains:

```gitignore
data/raw/
```

The data remain available to local Python scripts but are not included in Git commits. Preserve the original downloads and annotations; future harmonized outputs should be written separately, for example under `data/processed/`.
