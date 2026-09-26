"""Lazy, cached adapters for the project's heterogeneous vision checkpoints."""

import ast
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import OrderedDict
import gc
import json
import logging
import os
import re
from threading import RLock
import time
from io import BytesIO
from typing import Any

from PIL import Image, UnidentifiedImageError

from app.services.vision_config import VISION_MODELS, VisionModelConfig, resolve_model_name


logger = logging.getLogger(__name__)


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
    AUTO_MIN_CONFIDENCE = 0.5
    AUTO_THRESHOLDS = {
        "yolo_detection": 0.55,
        "yolo_segmentation": 0.55,
        "yolo_classification": 0.75,
        "mobilenetv3_classification": 0.75,
    }
    AUTO_MAX_WORKERS = 4
    DEFAULT_MODEL_CACHE_SIZE = 2

    def __init__(self) -> None:
        configured_size = os.getenv("VISION_MODEL_CACHE_SIZE", str(self.DEFAULT_MODEL_CACHE_SIZE))
        try:
            self.model_cache_size = max(1, int(configured_size))
        except ValueError:
            self.model_cache_size = self.DEFAULT_MODEL_CACHE_SIZE
        self._models: OrderedDict[str, Any] = OrderedDict()
        self._model_lock = RLock()

    def configs(self) -> list[VisionModelConfig]:
        return list(VISION_MODELS.values())

    @staticmethod
    def _metadata_classes(config: VisionModelConfig) -> list[str]:
        """Read the class names shipped with a checkpoint's existing metadata."""
        if not config.metadata_file or not config.metadata_file.is_file():
            return []
        try:
            text = config.metadata_file.read_text(encoding="utf-8")
            if config.metadata_file.suffix.lower() == ".json":
                payload = json.loads(text)
                if isinstance(payload, list):
                    return [str(value).strip() for value in payload if str(value).strip()]
                if isinstance(payload, dict) and isinstance(payload.get("classes"), list):
                    return [str(value).strip() for value in payload["classes"] if str(value).strip()]
                return []
            if config.metadata_file.suffix.lower() == ".csv":
                values = []
                for line in text.splitlines()[1:]:
                    columns = [column.strip() for column in line.split(",")]
                    if len(columns) > 1 and columns[1]:
                        values.append(columns[1])
                return values
            match = re.search(r"^names:\s*(\[.*\])\s*$", text, flags=re.MULTILINE)
            if match:
                values = ast.literal_eval(match.group(1))
                return [str(value).strip() for value in values if str(value).strip()]
            in_names = False
            values: list[str] = []
            for line in text.splitlines():
                if line.strip() == "names:":
                    in_names = True
                    continue
                if in_names:
                    item = re.match(r"^\s*-\s*[\"']?(.*?)[\"']?\s*$", line)
                    if item:
                        value = item.group(1).strip()
                        if value:
                            values.append(value)
                    else:
                        item = re.match(r"^\s*\d+\s*:\s*[\"']?(.*?)[\"']?\s*$", line)
                        if item and item.group(1).strip():
                            values.append(item.group(1).strip())
                        elif line and not line[0].isspace():
                            break
            return values
        except (OSError, SyntaxError, ValueError, json.JSONDecodeError):
            return []

    def supported_classes(self) -> list[str]:
        names: dict[str, str] = {}
        for config in self.configs():
            if not self.checkpoint_available(config):
                continue
            for raw_name in self._metadata_classes(config):
                key = " ".join(raw_name.replace("_", " ").replace("-", " ").split()).casefold()
                if key and key not in names:
                    names[key] = " ".join(raw_name.replace("_", " ").replace("-", " ").split())
        return sorted(names.values(), key=str.casefold)

    def supported_classes_for_model(self, name: str) -> list[str]:
        config = self._config(name)
        if not self.checkpoint_available(config):
            return []
        names: dict[str, str] = {}
        for raw_name in self._metadata_classes(config):
            key = " ".join(raw_name.replace("_", " ").replace("-", " ").split()).casefold()
            if key and key not in names:
                names[key] = " ".join(raw_name.replace("_", " ").replace("-", " ").split())
        return sorted(names.values(), key=str.casefold)

    def confidence_threshold(self, model_type: str) -> float:
        return self.AUTO_THRESHOLDS.get(model_type, self.AUTO_MIN_CONFIDENCE)

    def validate_selected_predictions(self, name: str, response: dict[str, Any], resolve_ingredient) -> dict[str, Any]:
        """Apply the same confidence/canonical gate to one explicitly selected model."""
        config = self._config(name)
        predictions: list[dict[str, Any]] = []
        threshold = self.confidence_threshold(config.model_type)
        for prediction in response.get("predictions", []):
            confidence = float(prediction.get("confidence", 0))
            canonical = resolve_ingredient(str(prediction.get("label", "")))
            logger.info(
                "vision selected-model candidate model=%s type=%s raw_label=%r confidence=%.4f threshold=%.4f canonical=%r",
                config.name, config.model_type, prediction.get("label"), confidence, threshold, canonical,
            )
            if confidence >= threshold and canonical:
                predictions.append({**prediction, "canonical": canonical})
        response = {**response, "predictions": predictions}
        if not predictions:
            response["status"] = "no_detection"
            response["error"] = "The selected model could not identify a supported ingredient confidently."
        return response

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

    def _release_model(self, model: Any) -> None:
        """Release references held by a model before the bounded cache drops it."""
        del model
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except (ImportError, RuntimeError):
            pass

    def _config(self, name: str) -> VisionModelConfig:
        canonical = resolve_model_name(name)
        try:
            return VISION_MODELS[canonical]
        except KeyError as exc:
            raise UnsupportedVisionModel(f"Unsupported vision model: {name}") from exc

    def _load(self, config: VisionModelConfig) -> Any:
        with self._model_lock:
            if config.name in self._models:
                model = self._models.pop(config.name)
                self._models[config.name] = model
                logger.info("vision model=%s cache_hit=true cache_size=%d", config.name, len(self._models))
                return model
            if len(self._models) >= self.model_cache_size:
                evicted_name, evicted_model = self._models.popitem(last=False)
                self._release_model(evicted_model)
                logger.info("vision model=%s cache_evicted=true cache_size=%d", evicted_name, len(self._models))
        if not self.checkpoint_available(config):
            raise VisionModelLoadError(f"Model checkpoint is missing: {config.checkpoint}")
        load_started = time.perf_counter()
        try:
            if config.model_type == "mobilenetv3_classification":
                model = self._load_spice_model(config)
            else:
                from ultralytics import YOLO
                model = YOLO(str(config.checkpoint), task=config.task)
        except Exception as exc:
            raise VisionModelLoadError(f"Could not load model '{config.name}': {exc}") from exc
        with self._model_lock:
            # Another request may have loaded this model while this request was
            # doing I/O; retain one canonical entry and keep the cache bounded.
            previous = self._models.pop(config.name, None)
            if previous is not None:
                self._release_model(previous)
            while len(self._models) >= self.model_cache_size:
                evicted_name, evicted_model = self._models.popitem(last=False)
                self._release_model(evicted_model)
                logger.info("vision model=%s cache_evicted=true cache_size=%d", evicted_name, len(self._models))
            self._models[config.name] = model
        logger.info(
            "vision model=%s cache_hit=false load_ms=%.2f cache_size=%d",
            config.name, (time.perf_counter() - load_started) * 1000, len(self._models),
        )
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
        processing_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "model": config.name, "module": config.module, "model_type": config.model_type,
            "status": "success", "predictions": predictions,
            "image_width": image.width, "image_height": image.height,
            "processing_ms": processing_ms,
        }

    def predict_auto(self, image_bytes: bytes, resolve_ingredient=None) -> dict[str, Any]:
        """Run local models and choose the strongest database-resolvable detection.

        ``resolve_ingredient`` is supplied by the API layer so this service does not
        own a database session.  A candidate is not eligible for automatic routing
        unless the current Jivanya data layer resolves its raw class to a canonical
        ingredient usable by recipe/nutrition matching.
        """
        candidates: list[tuple[float, int, str, dict[str, Any]]] = []
        failures: list[str] = []
        started = time.perf_counter()
        # Put broad, user-facing food detectors first.  The remaining specialist
        # models stay available as fallbacks, but are not paid for when a strong
        # canonical result has already been found.
        priority = (
            "fruits", "vegetables", "mutton", "chicken", "egg", "fish", "nuts",
            "grocery", "grocery_segmentation", "allergen", "farmer_seed",
            "indian_lentils", "coffee", "green_tea", "red_tea", "spices",
        )
        configured = {config.name: config for config in self.configs()}
        ordered_configs = [configured[name] for name in priority if name in configured]
        ordered_configs.extend(config for config in self.configs() if config.name not in priority)
        available = [config for config in ordered_configs if self.checkpoint_available(config)]

        def run(config: VisionModelConfig) -> tuple[VisionModelConfig, dict[str, Any]]:
            model_started = time.perf_counter()
            response = self.predict(config.name, image_bytes)
            logger.info(
                "vision invoked model=%s type=%s predictions=%d inference_ms=%.2f",
                config.name, config.model_type, len(response.get("predictions", [])),
                (time.perf_counter() - model_started) * 1000,
            )
            return config, response

        # There is no trustworthy image/category hint in the current registry.
        # Evaluate every available route in bounded parallel batches so a valid
        # early result cannot hide a correct specialist result, while avoiding
        # the previous long sequential wall time.  Ranking remains deterministic
        # because ``order`` comes from the registry priority above.
        with ThreadPoolExecutor(max_workers=min(self.AUTO_MAX_WORKERS, max(1, len(available)))) as executor:
            futures = {executor.submit(run, config): config for config in available}
            responses: list[tuple[int, VisionModelConfig, dict[str, Any]]] = []
            for future in as_completed(futures):
                config = futures[future]
                try:
                    _, response = future.result()
                except VisionServiceError as exc:
                    failures.append(str(exc))
                    logger.warning("vision model=%s failed during auto routing: %s", config.name, exc)
                    continue
                responses.append((ordered_configs.index(config), config, response))

        for order, config, response in sorted(responses, key=lambda item: item[0]):
            threshold = self.AUTO_THRESHOLDS.get(config.model_type, self.AUTO_MIN_CONFIDENCE)
            for prediction in response.get("predictions", []):
                confidence = float(prediction.get("confidence", 0))
                raw_label = str(prediction.get("label", "")).strip()
                canonical = resolve_ingredient(raw_label) if resolve_ingredient else raw_label
                logger.info(
                    "vision candidate model=%s type=%s raw_label=%r confidence=%.4f threshold=%.4f canonical=%r",
                    config.name, config.model_type, raw_label, confidence, threshold, canonical,
                )
                if confidence < threshold or not canonical:
                    continue
                # Compare confidence margins within task-specific thresholds rather
                # than treating detector boxes and classifier probabilities alike.
                calibrated = (confidence - threshold) / (1 - threshold)
                enriched = {**prediction, "canonical": canonical}
                candidates.append((calibrated, -order, config.name, enriched))
        if not candidates:
            return {
                "model": "auto",
                "module": "automatic local model routing",
                "model_type": "ensemble",
                "status": "no_detection",
                "predictions": [],
                "processing_ms": round((time.perf_counter() - started) * 1000, 2),
                "error": None if not failures else "No supported model produced a confident detection.",
            }
        _, _, selected_model, prediction = max(candidates)
        selected_config = VISION_MODELS[selected_model]
        logger.info(
            "vision selected model=%s type=%s raw_label=%r confidence=%.4f canonical=%r",
            selected_model, selected_config.model_type, prediction.get("label"),
            prediction.get("confidence", 0), prediction.get("canonical"),
        )
        return {
            "model": selected_model,
            "module": selected_config.module,
            "model_type": selected_config.model_type,
            "status": "success",
            "predictions": [prediction],
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
