
# Dataset Setup Guide

This repository does not redistribute the original datasets.
Download each dataset from its official source and store it
locally under `data/raw/`.

## 1. Directory Structure

The recommended project directory structure is:

```text
oil-palm-ripeness-cross-domain-benchmark/
├── configs/
│   ├── dataset1.yaml
│   └── class_mapping.yaml
├── data/
│   ├── raw/
│   │   ├── dataset1/
│   │   │   ├── train/
│   │   │   ├── valid/
│   │   │   └── test/
│   │   ├── dataset2/
│   │   │   └── yolov8/
│   │   │       ├── data.yaml
│   │   │       ├── train/
│   │   │       │   ├── images/
│   │   │       │   └── labels/
│   │   │       ├── valid/
│   │   │       │   ├── images/
│   │   │       │   └── labels/
│   │   │       └── test/
│   │   │           ├── images/
│   │   │           └── labels/
│   │   └── dataset3/
│   │       ├── FFBtrain/
│   │       └── FFBtest/
│   └── processed/
├── docs/
│   ├── dataset_setup.md
│   ├── dataset2_audit.md
│   ├── dataset3_audit.md
│   └── class_harmonization.md
├── results/
│   └── visualizations/
│       ├── dataset1/
│       ├── dataset2/
│       └── dataset3/
├── scripts/
│   ├── audit_dataset1.py
│   ├── audit_dataset2.py
│   ├── audit_dataset3.py
│   ├── validate_dataset2.py
│   ├── visualize_dataset1.py
│   └── visualize_dataset3.py
├── .gitignore
└── README.md
```

The `data/processed/` directory is reserved for future
harmonized datasets and experimental data.

Original dataset files must remain unchanged.

## 2. Dataset 1 — South Kalimantan Palm Oil Mill (2023)

### 2.1. Dataset Source

- Publication: [Annotated Datasets of Oil Palm Fruit Bunch Piles for Ripeness Grading Using Deep Learning](https://www.nature.com/articles/s41597-023-01958-x)
- Data repository: [Science Data Bank](https://doi.org/10.57760/sciencedb.j00001.00713)
- Domain: Palm oil mill
- Country: Indonesia
- Annotation format: YOLO object detection

### 2.2. Download and Extraction

Download the following archives from the data repository:

- `train_rev2.zip`
- `valid_rev2.zip`
- `test_rev2.zip`

Extract each archive and copy the inner `train`, `valid`,
and `test` directories into `data/raw/dataset1/`.

Do not include the outer `train_rev2`, `valid_rev2`,
or `test_rev2` directories.

The expected directory structure is:

```text
data/raw/dataset1/
├── train/
│   ├── image001.jpg
│   ├── image001.txt
│   └── ...
├── valid/
│   ├── image001.jpg
│   ├── image001.txt
│   └── ...
└── test/
    ├── image001.jpg
    ├── image001.txt
    └── ...
```

Image files and their corresponding annotation files
are stored in the same directory.

### 2.3. Annotation Format

Each annotation line follows the YOLO detection format:

```text
<class_id> <x_center> <y_center> <width> <height>
```

Bounding-box coordinates are normalized relative to
the image dimensions.

Each valid annotation line represents one annotated
object. A single image may contain multiple objects
from different classes.

### 2.4. Original Class Mapping

| Class ID | Class Name |
| ---: | --- |
| 0 | Empty Bunch |
| 1 | Under-ripe |
| 2 | Abnormal FFB |
| 3 | Ripe |
| 4 | Unripe |
| 5 | Over Ripe |

The provisional class mapping is documented in
[`configs/dataset1.yaml`](../configs/dataset1.yaml).

The mapping was established through object distribution
and visual inspection. Further confirmation against
the original class definitions is recommended.

### 2.5. Initial Audit Results

| Split | Images | Label Files | Annotated Objects |
| --- | ---: | ---: | ---: |
| Train | 2,908 | 2,908 | 10,140 |
| Validation | 835 | 835 | 3,008 |
| Test | 417 | 417 | 1,410 |
| **Total** | **4,160** | **4,160** | **14,558** |

The original publication reports 14,559 objects,
whereas the local audit counts 14,558 objects.

This one-object discrepancy remains unresolved.

Additional image integrity, annotation validity,
and duplicate checks are required before final
model training.

### 2.6. Reproduce the Audit

Run the following commands from the repository root:

```bash
python scripts/audit_dataset1.py
python scripts/visualize_dataset1.py
```

Visualization results are stored under:

```text
results/visualizations/dataset1/
```

## 3. Dataset 2 — Central Kalimantan Plantation (2025)

### 3.1. Dataset Source

- Publication: [Scientific Data (2025)](https://doi.org/10.1038/s41597-025-05227-x)
- Data repository: [Science Data Bank](https://doi.org/10.57760/SCIENCEDB.12647)
- Domain: Oil palm plantation
- Country: Indonesia
- Annotation format: YOLO object detection

### 3.2. Download and Extraction

Download the `preprocessed-ffb.zip` archive from
the data repository.

Extract the archive and place its YOLOv8 dataset
under `data/raw/dataset2/yolov8/`.

The expected directory structure is:

```text
data/raw/dataset2/yolov8/
├── data.yaml
├── train/
│   ├── images/
│   └── labels/
├── valid/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/
```

Unlike Dataset 1, images and annotation files
are stored in separate directories.

Each image must have a corresponding `.txt`
annotation file with the same filename stem.

### 3.3. Original Class Mapping

The original class mapping is provided by the
dataset's `data.yaml` file.

| Class ID | Class Name |
| ---: | --- |
| 0 | Abnormal |
| 1 | Flower |
| 2 | Ripe |
| 3 | Underripe |
| 4 | Unripe |

### 3.4. Initial Audit Results

| Split | Images | Label Files | Annotated Objects |
| --- | ---: | ---: | ---: |
| Train | 10,221 | 10,221 | 17,188 |
| Validation | 1,583 | 1,583 | 3,106 |
| Test | 765 | 765 | 1,531 |
| **Total** | **12,569** | **12,569** | **21,825** |

The initial audit reported:

- Zero annotation-format warnings.
- Zero corrupted images.
- Zero exact duplicate image groups.
- Zero exact duplicate groups across dataset splits.

However, exact duplicate detection using SHA-256
does not identify near-duplicate images, correlated
video frames, or visually similar augmentations.

The difference of 1,934 images between the local
archive and the previously reported dataset count
also remains unresolved.

See the [Dataset 2 Audit Report](dataset2_audit.md)
for detailed findings and limitations.

### 3.5. Reproduce the Audit

Run the following commands from the repository root:

```bash
python scripts/audit_dataset2.py
python scripts/validate_dataset2.py
```

Visualization results are stored under:

```text
results/visualizations/dataset2/
```

## 4. Dataset 3 — Malaysia Outdoor Oil Palm Dataset (2024)

### 4.1. Dataset Source

- Publication: Data in Brief (2024)
- Data repository: [Zenodo](https://zenodo.org/records/11114885)
- Domain: Outdoor oil palm plantation
- Country: Malaysia
- Annotation format: Image classification

### 4.2. Download and Extraction

Download the original dataset from its data repository.

The recommended dataset location is:

```text
data/raw/dataset3/
```

The original class-based directory structure
should be preserved:

```text
data/raw/dataset3/
├── FFBtrain/
│   ├── TrainDamaged/
│   ├── TrainEmpty/
│   ├── TrainOverripe/
│   ├── TrainRipe/
│   └── TrainUnripe/
└── FFBtest/
    ├── TestDamaged/
    ├── TestEmpty/
    ├── TestOverripe/
    ├── TestRipe/
    └── TestUnripe/
```

The existing Dataset 3 audit and visualization scripts
originally reference the extracted archive directory
at the repository root.

If the dataset is placed under `data/raw/dataset3/`,
update the `DATASET_PATH` variable in both scripts
before running them.

### 4.3. Original Class Distribution

| Class | Train | Test | Total |
| --- | ---: | ---: | ---: |
| Damaged | 12 | 3 | 15 |
| Empty | 9 | 3 | 12 |
| Overripe | 60 | 14 | 74 |
| Ripe | 160 | 41 | 201 |
| Unripe | 130 | 34 | 164 |
| **Total** | **371** | **95** | **466** |

The original dataset does not provide a separate
validation split.

### 4.4. Initial Audit Results

| Check | Result |
| --- | ---: |
| Total images | 466 |
| Valid images | 466 |
| Corrupted images | 0 |
| Unique SHA-256 hashes | 452 |
| Exact duplicate groups | 13 |
| Same-split duplicate groups | 9 |
| Cross-split duplicate groups | 4 |
| Recommended file exclusions | 14 |

The proposed duplicate exclusion policy retains
452 unique images.

These exclusions have been documented but have
not been physically applied to the raw dataset.

### 4.5. Distribution After Proposed Duplicate Exclusions

| Class | Train | Test | Total |
| --- | ---: | ---: | ---: |
| Damaged | 12 | 3 | 15 |
| Empty | 8 | 3 | 11 |
| Overripe | 58 | 14 | 72 |
| Ripe | 157 | 40 | 197 |
| Unripe | 123 | 34 | 157 |
| **Total** | **358** | **94** | **452** |

### 4.6. Annotation Limitations

The inspected dataset contains image-level class labels
organized through directory names.

No separate bounding-box annotation files were found
during the initial audit.

Bounding-box annotations must therefore be prepared
and validated before Dataset 3 can be included in
object detection experiments.

Image-level class labels must not be treated as
bounding-box annotations.

The number of annotated objects cannot be determined
until bounding-box annotation is completed.

See the [Dataset 3 Audit Report](dataset3_audit.md)
for detailed findings, duplicate handling policies,
and audit limitations.

### 4.7. Reproduce the Audit

Install the required audit dependencies if necessary:

```bash
python -m pip install pillow pandas
```

Ensure that the dataset paths in both scripts
match the local extraction directory.

Run:

```bash
python scripts/audit_dataset3.py
python scripts/visualize_dataset3.py
```

Visualization results are stored under:

```text
results/visualizations/dataset3/
```

## 5. Overall Dataset Summary

The following statistics describe the original
local datasets before harmonization and preprocessing.

| Dataset | Train Images | Validation Images | Test Images | Total Images | Annotated Objects |
| --- | ---: | ---: | ---: | ---: | ---: |
| Dataset 1 | 2,908 | 835 | 417 | 4,160 | 14,558 |
| Dataset 2 | 10,221 | 1,583 | 765 | 12,569 | 21,825 |
| Dataset 3 | 371 | N/A | 95 | 466 | N/A |
| **Total** | **13,500** | **2,418** | **1,277** | **17,195** | **36,383*** |

*The total annotated object count includes only
Dataset 1 and Dataset 2.

Dataset 3 object counts are unavailable because
bounding-box annotations have not been prepared.

## 6. Unified Class Taxonomy

### 6.1. Harmonization Strategy

The benchmark adopts a strict class intersection
strategy across the three datasets.

Only two shared classes are retained:

| Target Class ID | Class Name |
| ---: | --- |
| 0 | Unripe |
| 1 | Ripe |

Underripe is not merged into Unripe, and Overripe
is not merged into Ripe.

Other classes are excluded from the primary
two-class detection benchmark.

### 6.2. Dataset Class Mapping

| Dataset | Original Class | Original ID | Target ID |
| --- | --- | ---: | ---: |
| Dataset 1 | Unripe | 4 | 0 |
| Dataset 1 | Ripe | 3 | 1 |
| Dataset 2 | Unripe | 4 | 0 |
| Dataset 2 | Ripe | 2 | 1 |
| Dataset 3 | Unripe | N/A | 0 |
| Dataset 3 | Ripe | N/A | 1 |

Dataset 3 uses directory-based class labels rather
than numerical object detection class IDs.

The complete mapping is available in:

- [Class Mapping Configuration](../configs/class_mapping.yaml)
- [Class Harmonization Documentation](class_harmonization.md)

### 6.3. Expected Target Object Distribution

| Dataset | Unripe | Ripe | Total Objects |
| --- | ---: | ---: | ---: |
| Dataset 1 | 2,913 | 2,973 | 5,886 |
| Dataset 2 | 9,062 | 3,307 | 12,369 |
| **Total** | **11,975** | **6,280** | **18,255** |

These counts represent target annotations identified
during the initial audits.

Final counts may change after preprocessing,
annotation validation, and leakage mitigation.

For Dataset 3, the expected target image distribution
after applying the proposed duplicate exclusions is:

| Class | Train | Test | Total Images |
| --- | ---: | ---: | ---: |
| Unripe | 123 | 34 | 157 |
| Ripe | 157 | 40 | 197 |
| **Total** | **280** | **74** | **354** |

These values represent image counts, not annotated
object counts.

## 7. Preprocessing Policy

The following policies apply to the unified dataset:

1. Preserve all original raw dataset files.
2. Remap target classes to IDs 0 and 1.
3. Remove annotations belonging to non-target classes.
4. Retain images containing at least one target object.
5. Exclude images without target objects.
6. Preserve valid bounding-box coordinates.
7. Preserve original dataset splits unless documented
   leakage mitigation requires changes.
8. Record all excluded images and annotations.
9. Validate processed datasets before model training.
10. Store processed datasets under `data/processed/`.

Non-target objects may remain visible in retained
images and are treated as background under the
two-class detection task.

Excluding images without target objects limits the
evaluation of false positives on non-target-only scenes.

All models must follow the same preprocessing policy.

## 8. Model Compatibility

The processed datasets will support the following models:

- RF-DETR
- YOLO11
- YOLOv8

YOLO models will use YOLO-format annotations.

RF-DETR will use the annotation format required by
its training implementation, generated from the
same harmonized dataset.

Annotation conversion must preserve:

- Image membership.
- Semantic class mapping.
- Bounding-box geometry.
- Training, validation, and testing assignments.

All models must use equivalent dataset samples
for each benchmark experiment.

## 9. Audit and Preprocessing Status

| Task | Status |
| --- | --- |
| Dataset 1 initial audit | Completed |
| Dataset 1 visualization | Completed |
| Dataset 2 initial audit | Completed |
| Dataset 2 integrity validation | Completed |
| Dataset 2 visualization | Completed |
| Dataset 3 initial audit | Completed |
| Dataset 3 duplicate detection | Completed |
| Dataset 3 visualization | Completed |
| Unified class taxonomy | Defined |
| Dataset 1 preprocessing | Pending |
| Dataset 2 preprocessing | Pending |
| Dataset 3 bounding-box annotation | Pending |
| Dataset 3 preprocessing | Pending |
| Final dataset validation | Pending |
| Annotation format conversion | Pending |
| Experimental split preparation | Pending |

Initial audit completion does not establish that
the datasets are fully free from annotation errors
or data leakage.

## 10. Git Tracking

Raw and processed datasets must remain outside
version control.

Ensure that `.gitignore` contains:

```gitignore
data/raw/
data/processed/
```

The following files should be tracked:

- Dataset configuration files.
- Audit scripts.
- Preprocessing scripts.
- Validation scripts.
- Dataset documentation.
- Selected visualization samples.
- Experimental configurations.
- Benchmark result summaries.

Do not commit original dataset archives, complete
image collections, generated annotation collections,
or model weights.

Preserve the original downloads and annotations
to ensure reproducibility.
