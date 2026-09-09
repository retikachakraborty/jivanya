import os
import json
import torch
from torchvision import datasets, transforms, models
from torch import nn
from torch.utils.data import DataLoader

# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEST_DIR = os.path.join(
    BASE_DIR, "processed", "indian_spices", "test"
)

MODEL_PATH = os.path.join(
    BASE_DIR, "models", "indian_spices_mobilenetv3.pth"
)

# --------------------------------------------------
# Settings
# --------------------------------------------------
IMAGE_SIZE = 160
BATCH_SIZE = 8
NUM_WORKERS = 0

DEVICE = torch.device("cpu")

# --------------------------------------------------
# Transform
# --------------------------------------------------
test_transforms = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# --------------------------------------------------
# Load test dataset
# --------------------------------------------------
print("=" * 60)
print("JIVANYA - INDIAN SPICES TEST EVALUATION")
print("=" * 60)

test_dataset = datasets.ImageFolder(
    TEST_DIR,
    transform=test_transforms
)

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=NUM_WORKERS
)

classes = test_dataset.classes
num_classes = len(classes)

print(f"Test images: {len(test_dataset)}")
print(f"Number of classes: {num_classes}")
print()

# --------------------------------------------------
# Load model
# --------------------------------------------------
print("Loading trained model...")

model = models.mobilenet_v3_small(weights=None)

num_features = model.classifier[-1].in_features

model.classifier[-1] = nn.Linear(
    num_features,
    num_classes
)

checkpoint = torch.load(
    MODEL_PATH,
    map_location=DEVICE
)

model.load_state_dict(checkpoint["model_state_dict"])

model = model.to(DEVICE)
model.eval()

print("Model loaded successfully.")
print()

# --------------------------------------------------
# Evaluation
# --------------------------------------------------
correct = 0
total = 0

class_correct = [0] * num_classes
class_total = [0] * num_classes

print("Evaluating test set...")

with torch.no_grad():

    for images, labels in test_loader:

        images = images.to(DEVICE)
        labels = labels.to(DEVICE)

        outputs = model(images)

        _, predicted = torch.max(outputs, 1)

        total += labels.size(0)
        correct += (predicted == labels).sum().item()

        for label, prediction in zip(labels, predicted):

            label_index = label.item()

            class_total[label_index] += 1

            if prediction.item() == label_index:
                class_correct[label_index] += 1

# --------------------------------------------------
# Overall accuracy
# --------------------------------------------------
accuracy = 100.0 * correct / total

print()
print("=" * 60)
print("TEST RESULTS")
print("=" * 60)

print(f"Correct predictions: {correct}")
print(f"Total test images: {total}")
print(f"Test Accuracy: {accuracy:.2f}%")
print()

# --------------------------------------------------
# Per-class accuracy
# --------------------------------------------------
print("=" * 60)
print("PER-CLASS ACCURACY")
print("=" * 60)

for i, class_name in enumerate(classes):

    if class_total[i] > 0:
        class_accuracy = (
            100.0 * class_correct[i] / class_total[i]
        )
    else:
        class_accuracy = 0.0

    print(
        f"{i:2d}. {class_name:<20} "
        f"{class_correct[i]:3d}/{class_total[i]:3d} "
        f"({class_accuracy:6.2f}%)"
    )

print()
print("=" * 60)
print("EVALUATION FINISHED")
print("=" * 60)
