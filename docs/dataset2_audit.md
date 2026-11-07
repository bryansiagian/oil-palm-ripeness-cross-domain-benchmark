# Dataset 2 — Initial Audit Report

**Project:** Cross-Domain Oil Palm Fresh Fruit Bunch Ripeness Detection Benchmark (RF-DETR vs YOLO)  
**Dataset:** Dataset 2 — Central Kalimantan plantation (Scientific Data, 2025)  
**Local source:** `data/raw/dataset2/yolov8/`  
**Audit status:** **Initial audit completed with documented limitations**  
**Audit date:** 7 November 2026

## 1. Purpose and scope

This audit documents the local dataset's folder structure, YOLO annotation format, class mapping, object distribution, basic annotation validity, image integrity, exact-byte duplication checks, and a limited visual review. It establishes a reproducible baseline before taxonomy harmonization, preprocessing, and cross-domain model experiments.

The findings describe **the locally downloaded `preprocessed-ffb` archive**; they must not automatically be generalized to every version of the published dataset.

## 2. Dataset provenance and structure

- **Publication:** Scientific Data (2025), DOI: https://doi.org/10.1038/s41597-025-05227-x
- **Data repository referenced during setup:** https://doi.org/10.57760/SCIENCEDB.12647
- **Downloaded archive/folder name:** `preprocessed-ffb`
- **Annotation metadata:** `data/raw/dataset2/yolov8/data.yaml`

```text
data/raw/dataset2/
└── yolov8/
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

The labels use **YOLO object-detection format**, with one object per nonempty line:

```text
class_id x_center y_center width height
```

Bounding-box coordinates are normalized relative to image dimensions.

### Class mapping from `data.yaml`

The archive contains the following metadata:

```yaml
train: ../train/images
val: ../valid/images
test: ../test/images

nc: 5
names: ['Abnormal', 'Flower', 'Ripe', 'Underripe', 'Unripe']
```

| Class ID | Original class name |
| ---: | --- |
| 0 | Abnormal |
| 1 | Flower |
| 2 | Ripe |
| 3 | Underripe |
| 4 | Unripe |

**Important:** This is the original Dataset 2 class mapping. It has **not** yet been harmonized with Dataset 1 or Dataset 3. The relative paths in the original `data.yaml` should be checked against the chosen training working directory before model training.

## 3. Quantitative audit results

Generated with `python scripts/audit_dataset2.py` from the repository root.

| Split | Images | Label files | Annotated objects | Audit warnings |
| --- | ---: | ---: | ---: | ---: |
| Train | 10,221 | 10,221 | 17,188 | 0 |
| Valid | 1,583 | 1,583 | 3,106 | 0 |
| Test | 765 | 765 | 1,531 | 0 |
| **Total** | **12,569** | **12,569** | **21,825** | **0** |

### Class distribution

| Class ID | Class name | Train | Valid | Test | Total | Share of objects |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 0 | Abnormal | 2,802 | 318 | 139 | 3,259 | 14.93% |
| 1 | Flower | 2,673 | 251 | 182 | 3,106 | 14.23% |
| 2 | Ripe | 2,669 | 443 | 195 | 3,307 | 15.15% |
| 3 | Underripe | 2,605 | 305 | 181 | 3,091 | 14.16% |
| 4 | Unripe | 6,439 | 1,789 | 834 | 9,062 | 41.52% |
| **Total** | | **17,188** | **3,106** | **1,531** | **21,825** | **100%** |

**Observation:** `Unripe` accounts for approximately 41.5% of all annotated objects. This class imbalance should be considered when interpreting per-class performance, rather than relying only on aggregate metrics.

### Annotation checks performed

The audit script checked image/label stem correspondence, five-column annotation rows, numeric values, nonnegative integer class IDs, and normalized bounding-box coordinates including boundary checks. It reported **zero warnings** on the local files.

A zero-warning result applies only to these implemented checks; it does not establish that all semantic class assignments or bounding boxes are correct.

## 4. Image integrity and exact duplicate checks

Generated with `python scripts/validate_dataset2.py` from the repository root.

| Check | Result |
| --- | ---: |
| Images processed | 12,569 |
| Images failing Pillow verification | 0 |
| Groups of byte-identical images (SHA-256) | 0 |
| Groups of byte-identical images across splits | 0 |

**Interpretation:** No corrupt images or byte-identical duplicates were detected by these methods. SHA-256 does **not** identify near-duplicates, adjacent video frames, resized/recompressed copies, or visually similar augmentations. Consequently, these results do **not** establish that the train/validation/test splits are free of leakage.

## 5. Visual annotation review

The revised `scripts/validate_dataset2.py` creates three sample images per class under `results/visualizations/dataset2/class_0/` through `class_4/`, displaying **all bounding boxes and class labels** for each selected image.

| Class | Visual finding | Assessment |
| --- | --- | --- |
| 0 — Abnormal | The inspected examples were blurry and partly occluded; the abnormal condition could not be confidently confirmed. | Inconclusive; inspect more samples if this class is central to evaluation. |
| 1 — Flower | A sample box appeared to cover a flower/inflorescence structure; the image also contained an `Unripe` annotation. | Broadly consistent with the metadata. |
| 2 — Ripe | The principal box covered a fruit bunch; another `Unripe` box appeared near the image edge. | Plausible, but ripeness cannot be definitively established from this sample alone. |
| 3 — Underripe | A sample box covered a dark reddish-purple fruit bunch. | Broadly consistent; compare against `Unripe` examples when harmonizing classes. |
| 4 — Unripe | A sampled image also had a large `Underripe` box around the main bunch, while a smaller `Unripe` box lay at the lower-right edge. | Flag the small box for targeted annotation review; not yet proof of an incorrect label. |

**Sampling limitation:** Only a small, nonrepresentative set of visualizations was inspected. The script samples images by class and may select images containing multiple classes. The visual review does not certify the accuracy of all 21,825 object annotations.

## 6. Difference between local archive and previously reported paper counts

The following publication counts were used as a **previously reported reference** in the project discussion. Their exact table/version relationship to the downloaded archive still requires source-level reconciliation.

| Split | Previously reported reference | Local audit | Local minus reference |
| --- | ---: | ---: | ---: |
| Train | 10,207 | 10,221 | +14 |
| Valid | 2,896 | 1,583 | -1,313 |
| Test | 1,400 | 765 | -635 |
| **Total** | **14,503** | **12,569** | **-1,934** |

**Status: unresolved.** The local `preprocessed-ffb` archive contains 1,934 fewer images than the previously cited total. This difference must **not** be attributed to augmentation, filtering, or a different release without supporting documentation. The local counts are reproducible from the files currently available.

Before publication of benchmark results, record the downloaded archive's exact source/version, inspect its accompanying documentation, and verify which sample counts and split definitions are comparable to the paper.

## 7. Risks and limitations

1. **Potential near-duplicate leakage:** SHA-256 only detects byte-identical images; use perceptual hashing and/or embedding-based similarity checks across splits, with manual review of flagged pairs.
2. **Potential correlated frames:** Inspect filenames, acquisition sequence, and source-video or tree identifiers if available. Prefer grouping correlated images before any resplitting.
3. **Uncertain annotation quality:** Some sample boxes are hard to interpret or appear near image edges. Review flagged annotations without modifying the original raw data.
4. **Class imbalance:** `Unripe` represents approximately 41.5% of objects; report class-specific metrics.
5. **Unreconciled dataset counts:** The local archive and previously reported reference differ by 1,934 images.
6. **Cross-dataset taxonomy:** `Flower` is not automatically equivalent to `Empty Bunch` or `Over Ripe` in Dataset 1; mapping must be justified by definitions, not class IDs.

## 8. Conclusion and next actions

**Conclusion: Initial Dataset 2 audit completed with documented limitations.** The local archive has a consistent basic YOLO structure, 12,569 image/label pairs, 21,825 annotated objects across five classes, zero reported annotation-format warnings, zero Pillow verification failures, and zero byte-identical duplicate groups. The class mapping is explicitly provided in the archive's `data.yaml`.

**Not yet certified:** semantic correctness of all annotations, absence of near-duplicate or correlated-frame leakage, and reconciliation of the 1,934-image discrepancy.

**Recommended next steps:**

1. Preserve the raw archive unchanged and retain this report in version control.
2. Record the exact archive source/version and resolve or explicitly document the publication-count discrepancy.
3. Before final training/evaluation, run a cross-split near-duplicate/correlated-frame audit and review suspicious annotations.
4. Audit Dataset 3, then harmonize the three datasets' taxonomies and define leakage-aware experimental splits.

## 9. Reproduction

From the repository root:

```powershell
python scripts/audit_dataset2.py
python scripts/validate_dataset2.py
```

Expected local paths:

```text
scripts/audit_dataset2.py
scripts/validate_dataset2.py
data/raw/dataset2/yolov8/
results/visualizations/dataset2/
```

Raw dataset images and labels are not intended for Git commits. Commit the audit scripts and this report; keep any generated visualizations subject to dataset licensing and repository-size considerations.
