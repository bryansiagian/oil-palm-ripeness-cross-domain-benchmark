
# Class Taxonomy Harmonization

## 1. Objective

The three datasets used in this project have different
class definitions and annotation structures.

Class harmonization is required to establish a consistent
label space for comparing RF-DETR, YOLO11, and YOLOv8
across different oil palm domains.

## 2. Harmonization Strategy

This project adopts a strict class intersection strategy.

Only classes shared by all three datasets are retained:

- Unripe
- Ripe

Other classes are excluded from the primary benchmark.

Underripe is not merged into Unripe, and Overripe is not
merged into Ripe. This preserves the original distinction
between ripeness categories.

The shared class names are treated as compatible for the
benchmark, subject to further review of their definitions
and annotation quality.

## 3. Unified Class Taxonomy

| Class ID | Class Name |
| ---: | --- |
| 0 | Unripe |
| 1 | Ripe |

All models must use the same target class taxonomy.

## 4. Original Class Mapping

### Dataset 1

| Original ID | Original Class | Target ID |
| ---: | --- | --- |
| 0 | Empty Bunch | Excluded |
| 1 | Under-ripe | Excluded |
| 2 | Abnormal FFB | Excluded |
| 3 | Ripe | 1 |
| 4 | Unripe | 0 |
| 5 | Over Ripe | Excluded |

The mapping follows the existing dataset1.yaml
configuration, which was established through object
distribution and visual inspection.

### Dataset 2

| Original ID | Original Class | Target ID |
| ---: | --- | --- |
| 0 | Abnormal | Excluded |
| 1 | Flower | Excluded |
| 2 | Ripe | 1 |
| 3 | Underripe | Excluded |
| 4 | Unripe | 0 |

The original mapping follows the dataset's data.yaml file.

### Dataset 3

| Original Class | Target ID |
| --- | --- |
| Damaged | Excluded |
| Empty | Excluded |
| Overripe | Excluded |
| Ripe | 1 |
| Unripe | 0 |

Dataset 3 currently contains image-level class labels.

Bounding-box annotations must be prepared and validated
before this dataset can be included in object detection
experiments.

Image-level labels must not be treated as bounding-box
annotations.

## 5. Expected Target Class Distribution

The following counts are based on the initial dataset
audits, before final preprocessing and leakage checks.

| Dataset | Unripe | Ripe | Total | Unit |
| --- | ---: | ---: | ---: | --- |
| Dataset 1 | 2913 | 2973 | 5886 | Objects |
| Dataset 2 | 9062 | 3307 | 12369 | Objects |
| Dataset 3 | 164 | 201 | 365 | Images |

Dataset 3 is expected to retain 354 target-class images
after applying the proposed exact duplicate exclusions.

These image counts do not represent object counts.

Final dataset statistics will be generated after
preprocessing and validation.

## 6. Preprocessing Policy

The following rules apply to all datasets:

1. Preserve the original raw dataset files.
2. Store processed datasets under data/processed/.
3. Remap target annotations to class IDs 0 and 1.
4. Remove annotations belonging to non-target classes.
5. Retain images containing at least one target object.
6. Exclude images without target objects.
7. Preserve valid bounding-box coordinates.
8. Preserve original dataset splits unless leakage
   mitigation requires documented changes.
9. Record all exclusions and preprocessing decisions.
10. Validate processed annotations before training.

Non-target objects may remain visible in retained images.
These objects are treated as background under the
two-class detection task.

Excluding images without target objects limits the
evaluation of false positives on non-target-only scenes.

These policies must be applied consistently across all
models.

## 7. Model Compatibility

YOLO11 and YOLOv8 will use YOLO-format annotations.

RF-DETR will use the annotation format required by its
training implementation, with an explicit conversion
from the shared class taxonomy.

Format conversion must preserve the semantic class
mapping, image membership, and bounding-box geometry.

All models must use equivalent training, validation,
and testing samples for each experiment.

## 8. Limitations

- Dataset 1 requires additional integrity validation
  and confirmation of its original class definitions.
- Dataset 2 contains unresolved differences between
  local archive counts and previously reported counts.
- Dataset 3 requires bounding-box annotations.
- Near-duplicate and cross-split leakage checks remain
  necessary.
- Shared class names do not guarantee identical
  annotation criteria across datasets.
- The unified dataset does not represent all original
  ripeness and fruit condition categories.

## 9. Configuration

The machine-readable class mapping is available at:

configs/class_mapping.yaml

This configuration serves as the shared reference for
dataset preprocessing and model integration.

## 10. Status

Class harmonization has been defined.

Dataset preprocessing, annotation conversion, and
final validation will be implemented in subsequent
development stages.
