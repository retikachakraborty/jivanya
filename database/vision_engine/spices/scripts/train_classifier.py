import os
import json
import time
import torch
from torchvision import datasets, transforms, models
from torch import nn, optim
from torch.utils.data import DataLoader

# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TRAIN_DIR = os.path.join(BASE_DIR, "processed", "indian_spices", "train")
VAL_DIR = os.path.join(BASE_DIR, "processed", "indian_spices", "val")

MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "indian_spices_mobilenetv3.pth")
CLASSES_PATH = os.path.join(MODEL_DIR, "indian_spices_classes.json")

# --------------------------------------------------
# Settings for low-memory CPU environment
# --------------------------------------------------
IMAGE_SIZE = 160
BATCH_SIZE = 8
EPOCHS = 10
LEARNING_RATE = 0.001
NUM_WORKERS = 0

DEVICE = torch.device("cpu")

print("=" * 60)
print("JIVANYA - INDIAN SPICES CLASSIFIER")
print("=" * 60)
print(f"Device: {DEVICE}")
print(f"Image size: {IMAGE_SIZE}x{IMAGE_SIZE}")
print(f"Batch size: {BATCH_SIZE}")
print(f"Epochs: {EPOCHS}")
print()

# --------------------------------------------------
# Image transformations
# --------------------------------------------------
train_transforms = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

val_transforms = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# --------------------------------------------------
# Load datasets
# --------------------------------------------------
print("Loading datasets...")

train_dataset = datasets.ImageFolder(
    TRAIN_DIR,
    transform=train_transforms
)

val_dataset = datasets.ImageFolder(
    VAL_DIR,
    transform=val_transforms
)

print(f"Training images: {len(train_dataset)}")
print(f"Validation images: {len(val_dataset)}")
print(f"Number of classes: {len(train_dataset.classes)}")
print()

print("Classes:")
for i, class_name in enumerate(train_dataset.classes):
    print(f"{i}: {class_name}")

# --------------------------------------------------
# Save class names
# --------------------------------------------------
with open(CLASSES_PATH, "w") as f:
    json.dump(train_dataset.classes, f, indent=2)

print()
print(f"Class names saved to: {CLASSES_PATH}")

# --------------------------------------------------
# Data loaders
# --------------------------------------------------
train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=NUM_WORKERS
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=NUM_WORKERS
)

# --------------------------------------------------
# MobileNetV3-Small
# --------------------------------------------------
print()
print("Loading MobileNetV3-Small...")

model = models.mobilenet_v3_small(weights=None)

# Replace classifier for 19 spice classes
num_features = model.classifier[-1].in_features

model.classifier[-1] = nn.Linear(
    num_features,
    len(train_dataset.classes)
)

model = model.to(DEVICE)

# --------------------------------------------------
# Loss and optimizer
# --------------------------------------------------
criterion = nn.CrossEntropyLoss()

optimizer = optim.Adam(
    model.parameters(),
    lr=LEARNING_RATE
)

# --------------------------------------------------
# Training
# --------------------------------------------------
best_val_accuracy = 0.0

print()
print("=" * 60)
print("STARTING TRAINING")
print("=" * 60)

for epoch in range(EPOCHS):

    start_time = time.time()

    # -----------------------------
    # Training
    # -----------------------------
    model.train()

    running_loss = 0.0
    correct = 0
    total = 0

    for batch_index, (images, labels) in enumerate(train_loader):

        images = images.to(DEVICE)
        labels = labels.to(DEVICE)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(outputs, labels)

        loss.backward()

        optimizer.step()

        running_loss += loss.item()

        _, predicted = torch.max(outputs, 1)

        total += labels.size(0)
        correct += (predicted == labels).sum().item()

        if (batch_index + 1) % 100 == 0:
            print(
                f"Epoch {epoch + 1}/{EPOCHS} | "
                f"Batch {batch_index + 1}/{len(train_loader)}"
            )

    train_loss = running_loss / len(train_loader)
    train_accuracy = 100.0 * correct / total

    # -----------------------------
    # Validation
    # -----------------------------
    model.eval()

    val_correct = 0
    val_total = 0
    val_loss_total = 0.0

    with torch.no_grad():

        for images, labels in val_loader:

            images = images.to(DEVICE)
            labels = labels.to(DEVICE)

            outputs = model(images)

            loss = criterion(outputs, labels)

            val_loss_total += loss.item()

            _, predicted = torch.max(outputs, 1)

            val_total += labels.size(0)
            val_correct += (predicted == labels).sum().item()

    val_loss = val_loss_total / len(val_loader)
    val_accuracy = 100.0 * val_correct / val_total

    elapsed = time.time() - start_time

    print()
    print(
        f"Epoch {epoch + 1}/{EPOCHS} completed in "
        f"{elapsed / 60:.1f} minutes"
    )

    print(f"Train Loss: {train_loss:.4f}")
    print(f"Train Accuracy: {train_accuracy:.2f}%")
    print(f"Val Loss: {val_loss:.4f}")
    print(f"Val Accuracy: {val_accuracy:.2f}%")
    print()

    # -----------------------------
    # Save best model only
    # -----------------------------
    if val_accuracy > best_val_accuracy:

        best_val_accuracy = val_accuracy

        torch.save(
            {
                "model_state_dict": model.state_dict(),
                "classes": train_dataset.classes,
                "image_size": IMAGE_SIZE
            },
            MODEL_PATH
        )

        print(
            f"✓ Best model saved "
            f"(validation accuracy: {val_accuracy:.2f}%)"
        )

print()
print("=" * 60)
print("TRAINING FINISHED")
print("=" * 60)
print(f"Best validation accuracy: {best_val_accuracy:.2f}%")
print(f"Model saved to: {MODEL_PATH}")
print(f"Classes saved to: {CLASSES_PATH}")
