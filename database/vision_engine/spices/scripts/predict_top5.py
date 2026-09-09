import os
import json
import torch
from torchvision import transforms, models
from PIL import Image
from torch import nn

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

IMAGE_SIZE = 160
DEVICE = torch.device("cpu")

with open(CLASSES_PATH, "r") as f:
    classes = json.load(f)

model = models.mobilenet_v3_small(weights=None)

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

transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

image_path = "/home/mousumi/Pictures/Nutmeg-seeds-ground-spice.webp"

image = Image.open(image_path).convert("RGB")
image_tensor = transform(image).unsqueeze(0)

with torch.no_grad():
    outputs = model(image_tensor)

    probabilities = torch.softmax(
        outputs,
        dim=1
    )

    top_probabilities, top_indices = torch.topk(
        probabilities,
        k=5,
        dim=1
    )

print()
print("=" * 60)
print("JIVANYA - TOP 5 PREDICTIONS")
print("=" * 60)

for rank, (probability, index) in enumerate(
    zip(
        top_probabilities[0],
        top_indices[0]
    ),
    start=1
):
    print(
        f"{rank}. "
        f"{classes[index.item()]:<25} "
        f"{probability.item() * 100:.2f}%"
    )

print("=" * 60)
