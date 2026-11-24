
# Dataset Preprocessing Report

## 1. Objective

This preprocessing stage harmonizes Dataset 1 and Dataset 2
into a shared two-class object detection taxonomy for the
cross-domain oil palm ripeness benchmark.

The preprocessing pipeline ensures that all models use
consistent class definitions, annotation formats, and
dataset structures.

Dataset 3 is not included in this stage because bounding-box
annotations are still required.

## 2. Unified Class Taxonomy

| Class ID | Class Name |
|----------|------------|
| 0 | Unripe |
| 1 | Ripe |

The class mapping follows the strict intersection strategy
defined in `configs/class_mapping.yaml`.

### Dataset 1 Mapping

| Original ID | Original Class | Target ID |
|-------------|----------------|-----------|
| 0 | Empty Bunch | Excluded |
| 1 | Under-ripe | Excluded |
| 2 | Abnormal FFB | Excluded |
| 3 | Ripe | 1 |
| 4 | Unripe | 0 |
| 5 | Over Ripe | Excluded |

The original Dataset 1 class mapping remains subject to
confirmation against authoritative dataset metadata.

### Dataset 2 Mapping

| Original ID | Original Class | Target ID |
|-------------|----------------|-----------|
| 0 | Abnormal | Excluded |
| 1 | Flower | Excluded |
| 2 | Ripe | 1 |
| 3 | Underripe | Excluded |
| 4 | Unripe | 0 |

## 3. Preprocessing Methodology

The preprocessing pipeline performs the following steps:

1. Load the shared class mapping configuration.
2. Collect image and annotation files.
3. Verify image-label correspondence.
4. Check image integrity.
5. Validate YOLO annotation fields and coordinates.
6. Remove annotations belonging to non-target classes.
7. Remap retained annotations to the unified class IDs.
8. Exclude images without target objects.
9. Preserve images containing at least one target object.
10. Save the processed images and annotations.
11. Generate dataset configuration and summary reports.

Original bounding-box coordinate values are preserved.
The original train, validation, and test splits are
maintained during this preprocessing stage.

Raw dataset files are not modified.

## 4. Implementation

The preprocessing implementation consists of the following
files:

| File | Description |
|------|-------------|
| `scripts/preprocessing/__init__.py` | Package initialization |
| `scripts/preprocessing/common.py` | Shared preprocessing functions |
| `scripts/preprocessing/preprocess_dataset1.py` | Dataset 1 preprocessing entry point |
| `scripts/preprocessing/preprocess_dataset2.py` | Dataset 2 preprocessing entry point |

Both datasets use the same preprocessing logic while
supporting their different original directory structures.

## 5. Dataset 1 Results

### 5.1 Image Distribution

| Split | Original | Retained | Excluded |
|-------|---------:|---------:|---------:|
| Train | 2908 | 2046 | 862 |
| Valid | 835 | 578 | 257 |
| Test | 417 | 265 | 152 |
| Total | 4160 | 2889 | 1271 |

Image retention rate: 69.45%.

### 5.2 Object Distribution

| Split | Original | Retained | Removed |
|-------|---------:|---------:|--------:|
| Train | 10140 | 4147 | 5993 |
| Valid | 3008 | 1227 | 1781 |
| Test | 1410 | 512 | 898 |
| Total | 14558 | 5886 | 8672 |

Object retention rate: 40.43%.

### 5.3 Target Class Distribution

| Split | Unripe | Ripe | Total |
|-------|-------:|-----:|------:|
| Train | 2005 | 2142 | 4147 |
| Valid | 642 | 585 | 1227 |
| Test | 266 | 246 | 512 |
| Total | 2913 | 2973 | 5886 |

### 5.4 Images per Target Class

| Split | Unripe | Ripe |
|-------|-------:|-----:|
| Train | 776 | 1361 |
| Valid | 247 | 352 |
| Test | 107 | 167 |
| Total | 1130 | 1880 |

Image counts per class may overlap because one image can
contain both Unripe and Ripe objects.

### 5.5 Mixed-Class Images

A total of 1903 retained images originally contained both
target and non-target objects.

Non-target annotations were removed while the corresponding
images were preserved.

## 6. Dataset 2 Results

### 6.1 Image Distribution

| Split | Original | Retained | Excluded |
|-------|---------:|---------:|---------:|
| Train | 10221 | 6080 | 4141 |
| Valid | 1583 | 1337 | 246 |
| Test | 765 | 647 | 118 |
| Total | 12569 | 8064 | 4505 |

Image retention rate: 64.16%.

### 6.2 Object Distribution

| Split | Original | Retained | Removed |
|-------|---------:|---------:|--------:|
| Train | 17188 | 9108 | 8080 |
| Valid | 3106 | 2232 | 874 |
| Test | 1531 | 1029 | 502 |
| Total | 21825 | 12369 | 9456 |

Object retention rate: 56.67%.

### 6.3 Target Class Distribution

| Split | Unripe | Ripe | Total |
|-------|-------:|-----:|------:|
| Train | 6439 | 2669 | 9108 |
| Valid | 1789 | 443 | 2232 |
| Test | 834 | 195 | 1029 |
| Total | 9062 | 3307 | 12369 |

### 6.4 Images per Target Class

| Split | Unripe | Ripe |
|-------|-------:|-----:|
| Train | 4976 | 2653 |
| Valid | 1199 | 443 |
| Test | 569 | 194 |
| Total | 6744 | 3290 |

Image counts per class may overlap.

### 6.5 Mixed-Class Images

A total of 4747 retained images originally contained both
target and non-target objects.

The same filtering policy used for Dataset 1 was applied
to Dataset 2.

## 7. Combined Preprocessing Results

### 7.1 Overall Statistics

| Metric | Dataset 1 | Dataset 2 | Total |
|--------|----------:|----------:|------:|
| Original images | 4160 | 12569 | 16729 |
| Retained images | 2889 | 8064 | 10953 |
| Excluded images | 1271 | 4505 | 5776 |
| Original objects | 14558 | 21825 | 36383 |
| Retained objects | 5886 | 12369 | 18255 |
| Removed objects | 8672 | 9456 | 18128 |
| Mixed-class images | 1903 | 4747 | 6650 |

### 7.2 Combined Split Distribution

| Split | Images | Unripe | Ripe | Objects |
|-------|-------:|-------:|-----:|--------:|
| Train | 8126 | 8444 | 4811 | 13255 |
| Valid | 1915 | 2431 | 1028 | 3459 |
| Test | 912 | 1100 | 441 | 1541 |
| Total | 10953 | 11975 | 6280 | 18255 |

These statistics summarize both datasets without physically
merging their samples or changing their domain identities.

## 8. Class Distribution Analysis

Dataset 1 has a relatively balanced target class
distribution, with 2913 Unripe objects and 2973 Ripe objects.

Dataset 2 contains more Unripe objects than Ripe objects,
with 9062 and 3307 objects respectively.

The difference in class distribution is retained as part
of the original dataset characteristics.

No oversampling, undersampling, or data augmentation was
applied during preprocessing.

Class imbalance should be considered when interpreting
per-class detection performance and cross-domain results.

## 9. Output Directory Structure

Both processed datasets follow the same directory structure:

    data/processed/
    ├── dataset1/
    │   ├── data.yaml
    │   ├── train/
    │   │   ├── images/
    │   │   └── labels/
    │   ├── valid/
    │   │   ├── images/
    │   │   └── labels/
    │   └── test/
    │       ├── images/
    │       └── labels/
    └── dataset2/
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

Processed dataset files are excluded from Git tracking.

## 10. Reproduction

Install the required dependencies:

    python -m pip install pyyaml pillow

Run the preprocessing scripts from the repository root:

    python -m scripts.preprocessing.preprocess_dataset1
    python -m scripts.preprocessing.preprocess_dataset2

Existing output directories and summary reports must be
backed up or renamed before rerunning preprocessing.

## 11. Generated Reports

The preprocessing pipeline generates the following reports:

- `results/preprocessing/dataset1_summary.json`
- `results/preprocessing/dataset2_summary.json`

Each report contains:

- Original image and object counts.
- Retained and excluded image counts.
- Original and target class distributions.
- Removed annotation counts.
- Mixed-class image counts.
- Image counts per target class.
- Excluded filenames.
- Image and object retention rates.

## 12. Limitations

The current preprocessing stage does not establish that
the processed datasets are completely free from data leakage.

Exact duplicate, near-duplicate, and cross-split leakage
checks must be completed before final benchmark training.

Non-target objects may remain visible in retained images
without corresponding annotations. These objects are treated
as background under the current two-class taxonomy.

Images containing only non-target objects are excluded.
Therefore, the processed test sets do not fully represent
false-positive behavior on non-target-only scenes.

Dataset 3 requires bounding-box annotation and duplicate
handling before it can be integrated into the detection
benchmark.

## 13. Status

Dataset 1 and Dataset 2 preprocessing has been completed.

The retained object counts match the expected counts from
the initial dataset audits.

The processed datasets are ready for further validation
and preliminary model integration.

Final benchmark training remains subject to dataset
validation, leakage checks, annotation format conversion,
and experimental split preparation.
