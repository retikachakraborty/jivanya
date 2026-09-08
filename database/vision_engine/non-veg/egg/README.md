# Egg Vision Dataset

## Overview

This module contains the Non-Veg Egg vision dataset for detecting and classifying egg-related food items.

## Dataset Classes

| Class ID | Class Name |
|---:|---|
| 0 | egg |
| 1 | whole_egg_boiled |

## Dataset Split

| Split | Images | Labels |
|---|---:|---:|
| Train | 1,880 | 1,880 |
| Validation | 176 | 176 |
| Test | 91 | 91 |
| Total | 2,147 | 2,147 |

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
train: train/images
val: valid/images
test: test/images

nc: 2
names: ['egg', 'whole_egg_boiled']
