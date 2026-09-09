import os
import json
import torch
from torchvision import datasets, transforms, models
from torch import nn
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, confusion_matrix

# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEST_DIR = os.path.join(
    BASE_DIR,
    "processed",
    "indian_spices",
    "test"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "indian_spices_mobilenetv3.pth"
)

RESULTS_PATH = os.path.join(
    BASE_DIR,
    "models",
    "evaluation_results.json"
)

# --------------------------------------------------
# Settings
# --------------------------------------------------
IMAGE_SIZE = 160
BATCH_SIZE = 8
NUM_WORKERS = 0

DEVICE = torch.device("cpu")

# --------------------------------------------------
# Image transformation
# --------------------------------------------------
transform = transforms.Compose([
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
print("=" * 70)
print("JIVANYA - DETAILED INDIAN SPICES EVALUATION")
print("=" * 70)

test_dataset = datasets.ImageFolder(
    TEST_DIR,
    transform=transform
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
print(f"Classes: {num_classes}")

# --------------------------------------------------
# Load trained model
# --------------------------------------------------
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

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model = model.to(DEVICE)
model.eval()

print()
print("Model loaded successfully.")

# --------------------------------------------------
# Generate predictions
# --------------------------------------------------
all_labels = []
all_predictions = []

print()
print("Evaluating test set...")

with torch.no_grad():

    for images, labels in test_loader:

        images = images.to(DEVICE)
        labels = labels.to(DEVICE)

        outputs = model(images)

        _, predictions = torch.max(
            outputs,
            1
        )

        all_labels.extend(
            labels.cpu().numpy().tolist()
        )

        all_predictions.extend(
            predictions.cpu().numpy().tolist()
        )

# --------------------------------------------------
# Overall accuracy
# --------------------------------------------------
correct = sum(
    actual == predicted
    for actual, predicted in zip(
        all_labels,
        all_predictions
    )
)

total = len(all_labels)

incorrect = total - correct

accuracy = (
    100.0 * correct / total
)

print()
print("=" * 70)
print("OVERALL RESULT")
print("=" * 70)

print(f"Correct predictions : {correct}")
print(f"Incorrect predictions: {incorrect}")
print(f"Total test images   : {total}")
print(f"Test Accuracy       : {accuracy:.2f}%")

# --------------------------------------------------
# Classification report
# --------------------------------------------------
print()
print("=" * 70)
print("CLASSIFICATION REPORT")
print("=" * 70)

report = classification_report(
    all_labels,
    all_predictions,
    target_names=classes,
    digits=4,
    zero_division=0
)

print(report)

# --------------------------------------------------
# Confusion matrix
# --------------------------------------------------
cm = confusion_matrix(
    all_labels,
    all_predictions
)

print("=" * 70)
print("CONFUSION MATRIX")
print("=" * 70)

print("Rows = Actual class")
print("Columns = Predicted class")
print()

print(
    "     " +
    " ".join(
        f"{i:4d}"
        for i in range(num_classes)
    )
)

for i, row in enumerate(cm):

    print(
        f"{i:2d}: " +
        " ".join(
            f"{int(value):4d}"
            for value in row
        )
    )

# --------------------------------------------------
# Misclassified images
# --------------------------------------------------
print()
print("=" * 70)
print("MISCLASSIFICATIONS")
print("=" * 70)

misclassified = []

for index, (actual, predicted) in enumerate(
    zip(
        all_labels,
        all_predictions
    )
):

    if actual != predicted:

        image_path = test_dataset.samples[index][0]

        item = {
            "image": str(image_path),
            "actual": classes[actual],
            "predicted": classes[predicted]
        }

        misclassified.append(item)

        print(
            f"{len(misclassified):2d}. "
            f"Actual: {classes[actual]:<20} "
            f"Predicted: {classes[predicted]:<20}"
        )

# --------------------------------------------------
# Save results to JSON
# --------------------------------------------------
results = {
    "test_images": int(total),
    "correct": int(correct),
    "incorrect": int(incorrect),
    "accuracy_percent": float(
        round(accuracy, 2)
    ),
    "classes": classes,
    "misclassifications": misclassified
}

with open(
    RESULTS_PATH,
    "w"
) as f:

    json.dump(
        results,
        f,
        indent=2
    )

print()
print("=" * 70)
print("RESULTS SAVED")
print("=" * 70)

print(
    f"Detailed results saved to:\n"
    f"{RESULTS_PATH}"
)

print()
print("=" * 70)
print("EVALUATION COMPLETE")
print("=" * 70)
