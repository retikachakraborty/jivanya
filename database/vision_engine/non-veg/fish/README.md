# Fish Vision Dataset

## Overview

This module contains the Non-Veg Fish vision dataset for detecting and classifying different fish species.

## Dataset Classes

| Class ID | Class Name |
|---:|---|
| 0 | Bangus |
| 1 | Big-Head-Carp |
| 2 | Black-Spotted-Barb |
| 3 | Catfish |
| 4 | Climbing-Perch |
| 5 | Fourfinger-Threadfin |
| 6 | Freshwater-Eel |
| 7 | Glass-Perchlet |
| 8 | Goby |
| 9 | Gold-Fish |

## Dataset Split

| Split | Images | Labels |
|---|---:|---:|
| Train | 1,670 | 1,670 |
| Validation | 476 | 476 |
| Test | 238 | 238 |
| **Total** | **2,384** | **2,384** |

## Model Status

- Model status: Not trained
- Training epochs: Not applicable
- Model architecture: Not specified
- Model weights: Not available

No accuracy, precision, recall, or mAP values are reported because no trained model is currently available.

## Dataset Configuration

The dataset configuration is available at:

`processed/data.yaml`

```yaml
train: ../train/images
val: ../valid/images
test: ../test/images

nc: 10
names: ['Bangus', 'Big-Head-Carp', 'Black-Spotted-Barb', 'Catfish', 'Climbing-Perch', 'Fourfinger-Threadfin', 'Freshwater-Eel', 'Glass-Perchlet', 'Goby', 'Gold-Fish']
