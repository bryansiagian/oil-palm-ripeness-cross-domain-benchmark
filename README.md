
# Oil Palm Ripeness Cross-Domain Benchmark

A cross-domain object detection benchmark for oil palm
fresh fruit bunch (FFB) ripeness detection using RF-DETR,
YOLO11, and YOLOv8.

This project investigates the ability of object detection
models to generalize across different oil palm environments,
including palm oil mills and plantations in Indonesia
and Malaysia.

## Project Objectives

1. Harmonize class taxonomies across three public
   oil palm datasets.
2. Establish a consistent two-class object detection
   task across different domains.
3. Evaluate cross-domain generalization between
   palm oil mills and plantations.
4. Evaluate cross-country generalization between
   Indonesia and Malaysia.
5. Compare RF-DETR, YOLO11, and YOLOv8 in terms
   of detection accuracy and inference speed.
6. Establish a reproducible benchmark with consistent
   preprocessing and evaluation protocols.

## Datasets

The benchmark uses three publicly available datasets
from different geographical and environmental domains.

| Dataset | Location | Domain | Year | Annotation Format |
| --- | --- | --- | ---: | --- |
| Dataset 1 | South Kalimantan, Indonesia | Palm oil mill | 2023 | YOLO detection |
| Dataset 2 | Central Kalimantan, Indonesia | Plantation | 2025 | YOLO detection |
| Dataset 3 | Malaysia | Outdoor plantation | 2024 | Image classification |

### Dataset Sources

- Dataset 1: [Scientific Data (2023)](https://www.nature.com/articles/s41597-023-01958-x) — [Data Repository](https://doi.org/10.57760/sciencedb.j00001.00713)
- Dataset 2: [Scientific Data (2025)](https://doi.org/10.1038/s41597-025-05227-x) — [Data Repository](https://doi.org/10.57760/SCIENCEDB.12647)
- Dataset 3: Data in Brief (2024) — [Zenodo Repository](https://zenodo.org/records/11114885)

### Original Dataset Statistics

| Dataset | Train | Validation | Test | Total Images | Annotated Objects |
| --- | ---: | ---: | ---: | ---: | ---: |
| Dataset 1 | 2,908 | 835 | 417 | 4,160 | 14,558 |
| Dataset 2 | 10,221 | 1,583 | 765 | 12,569 | 21,825 |
| Dataset 3 | 371 | N/A | 95 | 466 | N/A |
| **Total** | **13,500** | **2,418** | **1,277** | **17,195** | **36,383*** |

*The total annotated object count includes only
Dataset 1 and Dataset 2.

Dataset 3 currently contains image-level class labels
and requires bounding-box annotations before inclusion
in object detection experiments.

The statistics above describe the original local datasets
before harmonization and final preprocessing.

## Unified Class Taxonomy

This project adopts a strict class intersection strategy
to establish a consistent label space across all datasets.

Only two shared ripeness classes are retained.

| Class ID | Class Name |
| ---: | --- |
| 0 | Unripe |
| 1 | Ripe |

Other classes are excluded from the primary benchmark.

Underripe is not merged into Unripe, and Overripe
is not merged into Ripe.

### Original-to-Target Class Mapping

| Dataset | Unripe Original ID | Ripe Original ID |
| --- | ---: | ---: |
| Dataset 1 | 4 | 3 |
| Dataset 2 | 4 | 2 |
| Dataset 3 | Directory-based label | Directory-based label |

All datasets will use the same target class taxonomy
after preprocessing.

The complete mapping and preprocessing policies are
available in:

- [Class Mapping Configuration](configs/class_mapping.yaml)
- [Class Harmonization Documentation](docs/class_harmonization.md)

### Expected Target Object Distribution

| Dataset | Unripe | Ripe | Total Objects |
| --- | ---: | ---: | ---: |
| Dataset 1 | 2,913 | 2,973 | 5,886 |
| Dataset 2 | 9,062 | 3,307 | 12,369 |
| **Total** | **11,975** | **6,280** | **18,255** |

Dataset 3 is expected to retain 354 target-class images
after applying the proposed duplicate exclusions.

Final image and object counts will be determined
after preprocessing and annotation validation.

## Models

The following object detection models are planned
for the benchmark.

| Model | Architecture Family |
| --- | --- |
| RF-DETR | Transformer-based object detection |
| YOLO11 | YOLO-based object detection |
| YOLOv8 | YOLO-based object detection |

All models will use the same target classes and
equivalent dataset samples for each experiment.

Model-specific annotation formats will be generated
from the shared harmonized dataset.

## Experimental Design

The benchmark will evaluate both in-domain and
cross-domain detection performance.

### In-Domain Evaluation

Models are trained and evaluated using different
splits from the same dataset.

This establishes a reference performance for each domain.

### Cross-Domain Evaluation

Models are trained using source-domain data and
evaluated on an unseen target domain.

This measures generalization under geographical
and environmental domain shifts.

### Leave-One-Dataset-Out Evaluation

The planned leave-one-dataset-out (LODO) experiments are:

| Experiment | Training Domains | Testing Domain |
| --- | --- | --- |
| LODO 1 | Dataset 2 + Dataset 3 | Dataset 1 |
| LODO 2 | Dataset 1 + Dataset 3 | Dataset 2 |
| LODO 3 | Dataset 1 + Dataset 2 | Dataset 3 |

Training and validation will use source-domain data only.

The held-out target domain must not be used for
model training, validation, or hyperparameter selection.

Experiments involving Dataset 3 are conditional on
the completion of its bounding-box annotations.

The final experimental protocol and dataset splits
will be documented before benchmark training.

## Evaluation Metrics

The benchmark will compare model accuracy,
generalization performance, and inference efficiency.

| Metric | Description |
| --- | --- |
| mAP@50 | Mean Average Precision at an IoU threshold of 0.50 |
| mAP@50:95 | Mean Average Precision across IoU thresholds from 0.50 to 0.95 |
| Domain Drop | Performance degradation between in-domain and cross-domain evaluation |
| FPS | Number of images processed per second |

Inference speed will be measured using consistent
hardware and benchmarking conditions.

## Dataset Preparation

The dataset preparation pipeline will include:

1. Dataset acquisition and extraction.
2. Initial dataset auditing.
3. Image and annotation validation.
4. Class taxonomy harmonization.
5. Target class remapping.
6. Duplicate detection and leakage mitigation.
7. Dataset preprocessing.
8. Annotation format conversion.
9. Experimental split preparation.
10. Final dataset validation.

Original datasets will remain unchanged.

Processed datasets will be stored separately under
`data/processed/`.

## Repository Structure

```text
oil-palm-ripeness-cross-domain-benchmark/
├── configs/
│   ├── dataset1.yaml
│   └── class_mapping.yaml
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

Raw and processed dataset directories are excluded
from version control.

Additional preprocessing, modeling, and evaluation
components will be added in subsequent development stages.

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/bryansiagian/oil-palm-ripeness-cross-domain-benchmark.git
cd oil-palm-ripeness-cross-domain-benchmark
```

### 2. Install Audit Dependencies

Python is required to run the dataset audit scripts.

Install the dependencies used by the existing
audit and visualization scripts:

```bash
python -m pip install pillow pandas pyyaml
```

Model-specific dependencies will be documented
when the modeling pipelines are available.

### 3. Download the Datasets

Follow the [Dataset Setup Guide](docs/dataset_setup.md)
to download the original datasets and configure
the required directory structure.

The datasets are not distributed through this repository.

### 4. Run Dataset Audits

Run the following commands from the repository root:

```bash
python scripts/audit_dataset1.py
python scripts/audit_dataset2.py
python scripts/audit_dataset3.py
```

Ensure that each script references the correct
local dataset directory.

### 5. Generate Dataset Visualizations

```bash
python scripts/visualize_dataset1.py
python scripts/validate_dataset2.py
python scripts/visualize_dataset3.py
```

Visualization results are stored under:

```text
results/visualizations/
```

## Documentation

| Document | Description |
| --- | --- |
| [Dataset Setup Guide](docs/dataset_setup.md) | Dataset sources, extraction, structure, and statistics |
| [Dataset 2 Audit Report](docs/dataset2_audit.md) | Annotation validation, image integrity, and duplicate findings |
| [Dataset 3 Audit Report](docs/dataset3_audit.md) | Image integrity, duplicate handling, and annotation limitations |
| [Class Harmonization](docs/class_harmonization.md) | Unified taxonomy, class mapping, and preprocessing policies |
| [Class Mapping Configuration](configs/class_mapping.yaml) | Machine-readable class mapping for all datasets |

## Project Status

### Phase 1 — Repository and Dataset Auditing

- [x] Repository initialization.
- [x] Dataset acquisition and directory setup.
- [x] Dataset 1 initial audit.
- [x] Dataset 1 visualization.
- [x] Dataset 2 initial audit.
- [x] Dataset 2 image integrity validation.
- [x] Dataset 2 visualization.
- [x] Dataset 3 initial audit.
- [x] Dataset 3 duplicate detection.
- [x] Dataset 3 visualization.

### Phase 2 — Class Harmonization and Preprocessing

- [x] Define the shared target classes.
- [x] Define the original-to-target class mapping.
- [x] Document class harmonization policies.
- [ ] Preprocess Dataset 1.
- [ ] Preprocess Dataset 2.
- [ ] Prepare Dataset 3 bounding-box annotations.
- [ ] Preprocess Dataset 3.
- [ ] Complete duplicate and leakage mitigation.
- [ ] Validate the processed datasets.
- [ ] Convert annotations into model-compatible formats.

### Phase 3 — Model Development

- [ ] Implement RF-DETR training pipeline.
- [ ] Implement YOLO11 training pipeline.
- [ ] Implement YOLOv8 training pipeline.
- [ ] Validate model input and output formats.
- [ ] Configure training environments.
- [ ] Perform initial model smoke tests.

### Phase 4 — Benchmark Experiments

- [ ] Finalize the experimental protocol.
- [ ] Prepare experimental dataset splits.
- [ ] Conduct in-domain training and evaluation.
- [ ] Conduct cross-domain training and evaluation.
- [ ] Conduct leave-one-dataset-out experiments.
- [ ] Measure inference speed.

### Phase 5 — Evaluation and Analysis

- [ ] Compare detection accuracy.
- [ ] Analyze cross-domain performance degradation.
- [ ] Compare inference efficiency.
- [ ] Generate benchmark tables and visualizations.
- [ ] Document experimental findings.
- [ ] Complete the final project report.

## Known Limitations

- Dataset 1 has an unresolved one-object difference
  between the local audit and the original publication.
- Dataset 1 class mapping requires further confirmation
  against the original class definitions.
- Dataset 2 has an unresolved difference of 1,934 images
  between the local archive and previously reported counts.
- Dataset 3 contains image-level labels and requires
  bounding-box annotations.
- Dataset 3 contains exact duplicates, including
  duplicates across training and testing splits.
- Near-duplicate and correlated-frame leakage checks
  have not been completed.
- The datasets contain different class distributions,
  environmental conditions, and annotation criteria.
- Shared class names do not guarantee identical
  ripeness annotation criteria across datasets.

These limitations will be addressed or documented
before final benchmark evaluation.

## Reproducibility

To ensure reproducibility, the project will maintain:

- Version-controlled dataset configurations.
- Documented class mapping policies.
- Reproducible preprocessing scripts.
- Consistent experimental dataset splits.
- Documented training configurations.
- Shared evaluation protocols.
- Recorded benchmark results.

Raw datasets, processed datasets, model weights,
and generated training outputs are excluded
from version control.

## Acknowledgments

This project uses publicly available oil palm datasets
published through Scientific Data, Data in Brief,
Science Data Bank, and Zenodo.

All original datasets remain subject to their
respective licenses and usage conditions.
