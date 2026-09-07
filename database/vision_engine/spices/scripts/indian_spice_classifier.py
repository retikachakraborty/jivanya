import os
import json

import torch
from torchvision import transforms, models
from PIL import Image
from torch import nn


class IndianSpiceClassifier:

    def __init__(self):

        # --------------------------------------------------
        # Paths
        # --------------------------------------------------
        base_dir = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        self.model_path = os.path.join(
            base_dir,
            "models",
            "indian_spices_mobilenetv3.pth"
        )

        self.classes_path = os.path.join(
            base_dir,
            "models",
            "indian_spices_classes.json"
        )

        # --------------------------------------------------
        # Settings
        # --------------------------------------------------
        self.image_size = 160
        self.device = torch.device("cpu")

        # --------------------------------------------------
        # Load classes
        # --------------------------------------------------
        with open(self.classes_path, "r") as f:
            self.classes = json.load(f)

        # --------------------------------------------------
        # Create model
        # --------------------------------------------------
        self.model = models.mobilenet_v3_small(
            weights=None
        )

        num_features = (
            self.model.classifier[-1].in_features
        )

        self.model.classifier[-1] = nn.Linear(
            num_features,
            len(self.classes)
        )

        # --------------------------------------------------
        # Load trained weights
        # --------------------------------------------------
        checkpoint = torch.load(
            self.model_path,
            map_location=self.device
        )

        self.model.load_state_dict(
            checkpoint["model_state_dict"]
        )

        self.model = self.model.to(
            self.device
        )

        self.model.eval()

        # --------------------------------------------------
        # Image preprocessing
        # --------------------------------------------------
        self.transform = transforms.Compose([
            transforms.Resize(
                (self.image_size, self.image_size)
            ),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    # ------------------------------------------------------
    # Predict one image
    # ------------------------------------------------------
    def predict(self, image_path):

        if not os.path.exists(image_path):
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        image = Image.open(
            image_path
        ).convert("RGB")

        image_tensor = self.transform(
            image
        ).unsqueeze(0)

        image_tensor = image_tensor.to(
            self.device
        )

        with torch.no_grad():

            outputs = self.model(
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

        predicted_class = self.classes[
            predicted_index.item()
        ]

        confidence_percentage = (
            confidence.item() * 100
        )

        return {
            "predicted_spice": predicted_class,
            "confidence": round(
                confidence_percentage,
                2
            )
        }
