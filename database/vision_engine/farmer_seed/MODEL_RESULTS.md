# Jivanya Vision Engine — Indian Ingredient Segmentation Model Results

## Overview

This document records the dataset preparation, training experiments, and final evaluation results for the Indian Ingredient Segmentation model.

## Dataset

- Source: Roboflow Universe — Sequel Farmer Dataset
- Images: 2,112
- Classes: 43
- Task: Instance segmentation
- Dataset split:
  - Training: 1,666 images
  - Validation: 297 images
  - Testing: 149 images

## Annotation Preparation

The dataset contained both YOLO bounding-box and segmentation annotations.

The preparation process included:

- Annotation validation
- Bounding-box conversion to rectangular polygons
- Segmentation annotation cleaning
- Class-distribution analysis

A total of 60,116 annotation lines were processed:

- Bounding boxes converted: 21,628
- Segmentation annotations retained: 38,488
- Invalid segmentation lines: 0
- Remaining 5-field labels: 0

## Class Imbalance

The dataset has severe class imbalance.

Chickpea was the dominant class, containing approximately 97.72% of all annotated objects.

Several balancing strategies were evaluated:

1. Original dataset
2. Balanced split
3. Object-balanced dataset
4. Oversampled dataset

The oversampled configuration produced the best performance.


The model is ready for YOLO segmentation inference.

## Status

- Dataset Preparation: Completed
- Annotation Cleaning: Completed
- Annotation Validation: Completed
- Class Imbalance Analysis: Completed
- Balancing Experiments: Completed
- Model Training: Completed
- Model Testing: Completed
- Final Model Selection: Completed
