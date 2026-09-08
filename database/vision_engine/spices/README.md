# Jivanya Vision Engine — Indian Spice Classification

## Overview

This module contains the Indian spice image dataset and the MobileNetV3-Small classification model.

## Dataset

- Source: Mendeley Data — Indian Spices Image Dataset
- Images: 10,991
- Classes: 19
- Task: Image classification
- License: CC BY 4.0

## Dataset Split

| Split | Images |
|---|---:|
| Training | 8,786 |
| Validation | 1,092 |
| Testing | 1,113 |
| **Total** | **10,991** |
## Classes

- Asafoetida
- Bay Leaf
- Black Cardamom
- Black Pepper
- Caraway seeds
- Cinnamom stick
- Cloves
- Coriander Seeds
- Cubeb Pepper
- Cumin seeds
- Dry Ginger
- Dry red Chilly
- Fennel seeds
- Green Cardamom
- Mace
- Nutmeg
- Poppy Seeds
- Star Anise
- Stone Flowers

## Metadata

metadata/classes.csv
metadata/image_manifest.csv

The image manifest records the image name, spice class, dataset split, and source.

## Final Model

- Architecture: MobileNetV3-Small
- Task: Image classification
- Image size: 160 × 160
- Training epochs: 10
- Training device: CPU

Final model: database/vision_engine/spices/models/indian_spices_mobilenetv3.pth

## Status

- Dataset Collection: Completed
- Dataset Preparation: Completed
- Model Training: Completed
- Model Testing: Completed
- Final Model Selection: Completed
