# Dataset 3 — Initial Audit Report

**Project:** Cross-Domain Oil Palm Fresh Fruit Bunch Ripeness Detection Benchmark (RF-DETR vs YOLO)  
**Dataset:** Dataset 3 — Malaysia Outdoor Oil Palm (Data in Brief, 2024)  
**Local source:** `MunirahRosbi-Outdoor-Tenera-Oil-Palm-Fruit-Image-b27ea70/`  
**Audit status:** Initial image integrity, exact duplicate, and local annotation-file inspection completed.  
**Audit date:** 9 November 2026

## 1. Purpose and Scope

This audit documents the local dataset structure, class distribution, image format, image integrity, image dimensions, exact-byte duplicate checks, and availability of separate annotation files.

The purpose is to establish a reproducible baseline for Dataset 3 before its potential use in the cross-domain oil palm ripeness detection benchmark.

The findings apply to the locally downloaded dataset version and should not automatically be generalized to other versions.

## 2. Dataset Provenance and Structure

- **Publication:** Data in Brief (2024)
- **Dataset repository:** https://zenodo.org/records/11114885
- **Dataset type:** Outdoor Tenera oil palm fruit images.
- **Original split structure:** Training and testing directories, organized by class.

The locally inspected directory structure is:

```text
MunirahRosbi-Outdoor-Tenera-Oil-Palm-Fruit-Image-b27ea70/
├── FFBtrain/
│   ├── TrainDamaged/
│   ├── TrainEmpty/
│   ├── TrainOverripe/
│   ├── TrainRipe/
│   └── TrainUnripe/
├── FFBtest/
│   ├── TestDamaged/
│   ├── TestEmpty/
│   ├── TestOverripe/
│   ├── TestRipe/
│   └── TestUnripe/
└── audit_results/
```

The dataset contains five original classes:

1. Damaged
2. Empty
3. Overripe
4. Ripe
5. Unripe

The original class names are preserved. They have not been modified or harmonized with other datasets.

## 3. Original Dataset Distribution

The initial folder-based image count is:

| Original Class | Train | Test | Total |
|---|---:|---:|---:|
| Damaged | 12 | 3 | 15 |
| Empty | 9 | 3 | 12 |
| Overripe | 60 | 14 | 74 |
| Ripe | 160 | 41 | 201 |
| Unripe | 130 | 34 | 164 |
| **Total** | **371** | **95** | **466** |

**Observation:** Ripe is the largest class, with 201 images (approximately 43.13% of the original dataset). Empty is the smallest class, with 12 images (approximately 2.58%).

The dataset has an existing training and testing split. No validation split was identified in the inspected directory structure.

These counts represent images organized by class folders, not annotated object instances.

## 4. Image Integrity and Format Validation

The audit used Pillow to verify image readability, file format, color mode, and image dimensions.

| Check | Result |
|---|---:|
| Total images checked | 466 |
| Valid images | 466 |
| Corrupted images | 0 |
| JPEG images | 466 |
| RGB images | 466 |
| `.jpg` extension | 389 |
| `.JPG` extension | 77 |

**Interpretation:** All 466 inspected files passed image verification. All files were identified as JPEG images in RGB color mode.

The difference between `.jpg` and `.JPG` is only the capitalization of the file extension, not a difference in image format.

### 4.1. Image Dimension Distribution

| Width × Height | Number of Images |
|---|---:|
| 757 × 568 | 233 |
| 4032 × 3024 | 80 |
| 2400 × 3200 | 63 |
| 2250 × 4000 | 31 |
| 3024 × 4032 | 28 |
| 3200 × 2400 | 23 |
| 824 × 464 | 6 |
| 2756 × 2381 | 1 |
| 4160 × 3120 | 1 |
| **Total** | **466** |

**Observation:** The dataset contains images with different resolutions and aspect ratios. A consistent resizing and preprocessing strategy will therefore be required before model training and evaluation.

## 5. Exact Duplicate Detection (SHA-256)

An exact duplicate audit was conducted using SHA-256 hashing to identify byte-identical image files.

| Check | Result |
|---|---:|
| Total images hashed | 466 |
| Unique SHA-256 hashes | 452 |
| Duplicate hash groups | 13 |
| Images in duplicate groups | 27 |
| Duplicate groups within the same split | 9 |
| Duplicate groups across Train and Test | 4 |
| Files involved in cross-split duplicates | 9 |
| Files involved in same-split duplicates | 18 |

### 5.1. Cross-Split Duplicate Groups

Four duplicate groups were identified across the training and testing splits.

| Group | Class | Train Files | Test Files |
|---|---|---:|---:|
| 1 | Unripe | 2 | 1 |
| 2 | Unripe | 1 | 1 |
| 3 | Ripe | 1 | 1 |
| 4 | Unripe | 1 | 1 |
| **Total** | | **5** | **4** |

The first group contains three identical files: two in the training split and one in the testing split. The remaining groups each contain one training image and one testing image.

**Interpretation:** The presence of byte-identical images across the training and testing splits represents a potential data leakage risk. Such overlap may affect the reliability of model evaluation if the same image is used for both training and testing.

### 5.2. Same-Split Duplicate Groups

Nine additional duplicate groups were identified within the same split.

| Split | Duplicate Groups | Files Involved |
|---|---:|---:|
| Train | 8 | 16 |
| Test | 1 | 2 |
| **Total** | **9** | **18** |

These groups contain byte-identical images located within either the training or testing split. They do not create cross-split overlap, but retaining multiple identical copies could unnecessarily increase the number of repeated samples.

### 5.3. Combined Duplicate Handling

The cross-split and same-split duplicate findings were combined into a single exclusion manifest.

The proposed handling policy is:

1. For cross-split duplicates, retain the testing image or images and recommend excluding identical copies from the training split.
2. For same-split duplicates, retain one representative image and recommend excluding the additional identical copies.
3. Preserve the original training and testing assignments.
4. Record all recommended exclusions in a CSV manifest without deleting or modifying the original images.

| Duplicate Type | Groups | Recommended Exclusions |
|---|---:|---:|
| Cross-split duplicates | 4 | 5 |
| Same-split duplicates | 9 | 9 |
| **Total** | **13** | **14** |

The combined handling results are:

| Metric | Result |
|---|---:|
| Original images | 466 |
| Recommended exclusions | 14 |
| Remaining images | 452 |
| Remaining unique SHA-256 hashes | 452 |
| Remaining exact duplicate groups | 0 |

**Interpretation:** After applying the proposed exclusion policy to the audit records, all 452 remaining images have unique SHA-256 hashes. No byte-identical duplicates remain in the proposed experimental dataset configuration.

The 14 exclusions are recommendations recorded in the manifest. They have not been physically deleted from the original dataset.

### 5.4. Dataset Distribution After Proposed Exclusions

| Class | Train | Test | Total | Percentage |
|---|---:|---:|---:|---:|
| Damaged | 12 | 3 | 15 | 3.32% |
| Empty | 8 | 3 | 11 | 2.43% |
| Overripe | 58 | 14 | 72 | 15.93% |
| Ripe | 157 | 40 | 197 | 43.58% |
| Unripe | 123 | 34 | 157 | 34.73% |
| **Total** | **358** | **94** | **452** | **100%** |

**Observation:** Ripe remains the largest class, with 197 images (43.58%), while Empty remains the smallest class, with 11 images (2.43%). The class distribution is imbalanced and should be considered when interpreting model evaluation results.

The proposed experimental configuration contains 358 training images and 94 testing images.

### 5.5. Duplicate Audit Output Files

The duplicate audit generated the following files under `audit_results/`:

- `dataset3_sha256_hashes.csv`
- `dataset3_duplicates.csv`
- `dataset3_cross_split_duplicates.csv`
- `dataset3_train_exclusion_manifest.csv`
- `dataset3_same_split_duplicates.csv`
- `dataset3_same_split_duplicate_manifest.csv`
- `dataset3_combined_exclusion_manifest.csv`

The combined exclusion manifest contains the recommended files to exclude and the corresponding duplicate-handling reasons.

## 6. Annotation File Inspection

A recursive inspection was conducted to identify possible separate annotation or metadata files in the downloaded dataset directory.

The inspection covered the following file extensions:

- `.txt`
- `.xml`
- `.json`
- `.csv`
- `.yaml`
- `.yml`

The `audit_results/` directory was excluded from this scan to avoid counting generated audit reports as original dataset annotations.

**Inspection result:**

| Check | Result |
|---|---:|
| Separate annotation/metadata files found | 0 |
| Bounding-box annotation files identified | 0 |

**Interpretation:** No separate annotation files were found in the inspected local dataset directory.

The available images are organized by class folders, indicating a folder-based image classification structure. The local inspection did not identify YOLO, Pascal VOC, COCO, or other separate bounding-box annotation files.

This result does not prove that annotations are unavailable in every possible supplementary source. It establishes only that no matching separate annotation files were found in the inspected local directory.

Consequently, the dataset cannot be treated as an already annotated object-detection dataset based on the inspected files alone.

## 7. Audit Limitations

1. **Annotation availability:** No separate annotation files were identified in the local directory. The images are organized by class folders rather than accompanied by identified bounding-box annotations.
2. **Proposed duplicate exclusions:** The 14 recommended exclusions have been recorded in a manifest but have not been physically removed from the original dataset.
3. **Near-duplicate images:** SHA-256 detects byte-identical files only. It does not identify resized, recompressed, or visually similar images.
4. **No validation split identified:** The inspected structure contains training and testing directories only.
5. **Different image dimensions:** Image preprocessing must account for varying resolutions and aspect ratios.
6. **Class imbalance:** The five classes have different sample counts, with Ripe substantially more represented than Empty.
7. **Semantic label verification:** This audit verifies folder names and image-file properties. It does not independently establish the biological correctness of every class label.

## 8. Conclusion and Next Actions

**Conclusion: Initial Dataset 3 image integrity, exact duplicate, and local annotation-file audits completed.**

The locally inspected dataset contains 466 readable JPEG images across five original classes: Damaged, Empty, Overripe, Ripe, and Unripe. All inspected images use RGB color mode, and no corrupted files were identified.

The SHA-256 audit identified 13 duplicate groups involving 27 files. These consist of four cross-split duplicate groups and nine same-split duplicate groups.

A combined exclusion manifest recommends excluding 14 files. Under this proposed policy, the experimental dataset configuration contains 452 images, comprising 358 training images and 94 testing images, with 452 unique SHA-256 hashes.

The local annotation inspection found no separate bounding-box annotation files. Therefore, the dataset is currently documented as a folder-based image classification dataset, not as an already annotated object-detection dataset.

**Audit completion statement:** The initial local image integrity, class-folder distribution, exact-byte duplicate, and annotation-file presence checks have been completed. This does not certify the absence of near-duplicate images, the semantic correctness of every class label, or the availability of annotations outside the inspected directory.

### Recommended follow-up considerations

1. Preserve the original downloaded dataset and use the combined exclusion manifest when constructing the deduplicated experimental configuration.
2. Obtain team agreement before applying the proposed exclusion policy to model experiments.
3. Consider perceptual or visual near-duplicate inspection if stronger leakage assessment is required.
4. Consult the dataset publication or supplementary materials if further confirmation of annotation availability is needed.
5. If the project requires object detection, determine whether additional bounding-box annotation work is necessary before using Dataset 3 for that task.

## 9. Reproduction and Audit Outputs

The audit was conducted using the `audit_dataset3.ipynb` notebook in the local Dataset 3 directory.

The audit outputs are stored in:

```text
audit_results/
├── dataset3_sha256_hashes.csv
├── dataset3_duplicates.csv
├── dataset3_cross_split_duplicates.csv
├── dataset3_train_exclusion_manifest.csv
├── dataset3_same_split_duplicates.csv
├── dataset3_same_split_duplicate_manifest.csv
└── dataset3_combined_exclusion_manifest.csv
```

The combined exclusion manifest can be used to reproduce the proposed 452-image experimental configuration.

The original downloaded dataset files were preserved without modification.