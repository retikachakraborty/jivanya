import os
import json
import argparse

import torch
from torchvision import transforms, models
from PIL import Image
from torch import nn


# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "indian_spices_mobilenetv3.pth"
)

CLASSES_PATH = os.path.join(
    BASE_DIR,
    "models",
    "indian_spices_classes.json"
)


# --------------------------------------------------
# Settings
# --------------------------------------------------
IMAGE_SIZE = 160
DEVICE = torch.device("cpu")


# --------------------------------------------------
# Load classes
# --------------------------------------------------
with open(CLASSES_PATH, "r") as f:
    classes = json.load(f)


# --------------------------------------------------
# Load model
# --------------------------------------------------
model = models.mobilenet_v3_small(
    weights=None
)

num_features = model.classifier[-1].in_features

model.classifier[-1] = nn.Linear(
    num_features,
    len(classes)
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


# --------------------------------------------------
# Image transformation
# --------------------------------------------------
transform = transforms.Compose([
    transforms.Resize(
        (IMAGE_SIZE, IMAGE_SIZE)
    ),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# --------------------------------------------------
# Prediction function
# --------------------------------------------------
def predict(image_path):

    image = Image.open(
        image_path
    ).convert("RGB")

    image_tensor = transform(
        image
    ).unsqueeze(0)

    image_tensor = image_tensor.to(
        DEVICE
    )

    with torch.no_grad():

        outputs = model(
            image_tensor
        )

        probabilities = torch.softmax(
            outputs,
            dim=1
        )

        confidence, predicted_index = torch.max(
            probabilities,
            1
        )

    predicted_class = classes[
        predicted_index.item()
    ]

    confidence_percentage = (
        confidence.item() * 100
    )

    return (
        predicted_class,
        confidence_percentage
    )


# --------------------------------------------------
# Main
# --------------------------------------------------
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Jivanya Indian Spice Classifier"
    )

    parser.add_argument(
        "image",
        help="Path to the spice image"
    )

    args = parser.parse_args()

    if not os.path.exists(args.image):

        print(
            f"ERROR: Image not found: {args.image}"
        )

        raise SystemExit(1)

    print()
    print("=" * 60)
    print("JIVANYA - INDIAN SPICE CLASSIFIER")
    print("=" * 60)

    print()
    print(f"Image: {args.image}")

    predicted_class, confidence = predict(
        args.image
    )

    print()
    print("=" * 60)
    print("PREDICTION")
    print("=" * 60)

    print(
        f"Predicted Spice : {predicted_class}"
    )

    print(
        f"Confidence      : {confidence:.2f}%"
    )

    print("=" * 60)
    print()
