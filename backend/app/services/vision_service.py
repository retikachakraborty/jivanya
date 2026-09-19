"""Lazy, cached adapters for the project's heterogeneous vision checkpoints."""

import json
import time
from io import BytesIO
from typing import Any

from PIL import Image, UnidentifiedImageError

from app.services.vision_config import VISION_MODELS, VisionModelConfig, resolve_model_name


class VisionServiceError(RuntimeError):
    pass


class UnsupportedVisionModel(VisionServiceError):
    pass


class InvalidVisionImage(VisionServiceError):
    pass


class VisionModelLoadError(VisionServiceError):
    pass


class VisionInferenceError(VisionServiceError):
    pass


class VisionService:
    MAX_IMAGE_BYTES = 10 * 1024 * 1024

    def __init__(self) -> None:
        self._models: dict[str, Any] = {}

    def configs(self) -> list[VisionModelConfig]:
        return list(VISION_MODELS.values())

    @staticmethod
    def checkpoint_available(config: VisionModelConfig) -> bool:
        """Treat an unhydrated Git-LFS pointer as unavailable, not as a model."""
        if not config.checkpoint.is_file() or config.checkpoint.stat().st_size < 1024:
            return False
        try:
            with config.checkpoint.open("rb") as handle:
                header = handle.read(80)
            return not header.startswith(b"version https://git-lfs.github.com/spec/v1")
        except OSError:
            return False

    def is_loaded(self, name: str) -> bool:
        return resolve_model_name(name) in self._models

    def _config(self, name: str) -> VisionModelConfig:
        canonical = resolve_model_name(name)
        try:
            return VISION_MODELS[canonical]
        except KeyError as exc:
            raise UnsupportedVisionModel(f"Unsupported vision model: {name}") from exc

    def _load(self, config: VisionModelConfig) -> Any:
        if config.name in self._models:
            return self._models[config.name]
        if not self.checkpoint_available(config):
            raise VisionModelLoadError(f"Model checkpoint is missing: {config.checkpoint}")
        try:
            if config.model_type == "mobilenetv3_classification":
                model = self._load_spice_model(config)
            else:
                from ultralytics import YOLO
                model = YOLO(str(config.checkpoint), task=config.task)
        except Exception as exc:
            raise VisionModelLoadError(f"Could not load model '{config.name}': {exc}") from exc
        self._models[config.name] = model
        return model

    @staticmethod
    def _load_spice_model(config: VisionModelConfig) -> dict[str, Any]:
        import torch
        from torch import nn
        from torchvision import models, transforms

        with config.classes_file.open(encoding="utf-8") as handle:
            classes = json.load(handle)
        model = models.mobilenet_v3_small(weights=None)
        model.classifier[-1] = nn.Linear(model.classifier[-1].in_features, len(classes))
        checkpoint = torch.load(config.checkpoint, map_location=torch.device("cpu"))
        model.load_state_dict(checkpoint["model_state_dict"])
        model.eval()
        return {"model": model, "classes": classes, "transform": transforms.Compose([
            transforms.Resize((160, 160)), transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])}

    @staticmethod
    def _image(image_bytes: bytes) -> Image.Image:
        if not image_bytes:
            raise InvalidVisionImage("Image upload is empty")
        if len(image_bytes) > VisionService.MAX_IMAGE_BYTES:
            raise InvalidVisionImage("Image upload exceeds the 10 MB limit")
        try:
            image = Image.open(BytesIO(image_bytes))
            image.verify()
            image = Image.open(BytesIO(image_bytes)).convert("RGB")
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise InvalidVisionImage("Uploaded file is not a valid image") from exc
        return image

    @staticmethod
    def _name(names: Any, index: int) -> str:
        return str(names[index]) if isinstance(names, (list, tuple)) else str(names.get(index, index))

    def predict(self, name: str, image_bytes: bytes) -> dict[str, Any]:
        config = self._config(name)
        image = self._image(image_bytes)
        started = time.perf_counter()
        try:
            model = self._load(config)
            if config.model_type == "mobilenetv3_classification":
                predictions = self._predict_spices(model, image)
            else:
                predictions = self._predict_yolo(model, image, config)
        except VisionServiceError:
            raise
        except Exception as exc:
            raise VisionInferenceError(f"Inference failed for '{config.name}': {exc}") from exc
        return {
            "model": config.name, "module": config.module, "model_type": config.model_type,
            "status": "success", "predictions": predictions,
            "image_width": image.width, "image_height": image.height,
            "processing_ms": round((time.perf_counter() - started) * 1000, 2),
        }

    @staticmethod
    def _predict_spices(bundle: dict[str, Any], image: Image.Image) -> list[dict[str, Any]]:
        import torch
        tensor = bundle["transform"](image).unsqueeze(0)
        with torch.no_grad():
            probabilities = torch.softmax(bundle["model"](tensor), dim=1)
            confidence, index = torch.max(probabilities, 1)
        return [{"label": bundle["classes"][index.item()], "confidence": float(confidence.item())}]

    @classmethod
    def _predict_yolo(cls, model: Any, image: Image.Image, config: VisionModelConfig) -> list[dict[str, Any]]:
        results = model.predict(source=image, imgsz=224 if config.task == "classify" else 640,
                                device="cpu", verbose=False, save=False)
        result = results[0]
        if config.task == "classify":
            if result.probs is None:
                return []
            return [{"label": cls._name(result.names, int(result.probs.top1)),
                     "confidence": float(result.probs.top1conf.item())}]
        predictions: list[dict[str, Any]] = []
        if result.boxes is None:
            return predictions
        masks = result.masks.xy if config.task == "segment" and result.masks is not None else None
        for position, (box, class_id, confidence) in enumerate(zip(
                result.boxes.xyxy.cpu().tolist(), result.boxes.cls.cpu().tolist(), result.boxes.conf.cpu().tolist())):
            predictions.append({"label": cls._name(result.names, int(class_id)),
                                "confidence": float(confidence), "bbox": [float(v) for v in box],
                                "segmentation": [[float(x), float(y)] for x, y in masks[position]] if masks is not None else None})
        return predictions


vision_service = VisionService()
