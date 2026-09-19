"""Central registry for the model checkpoints shipped with Jivanya."""

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
VISION_ROOT = PROJECT_ROOT / "database" / "vision_engine"


@dataclass(frozen=True)
class VisionModelConfig:
    name: str
    module: str
    model_type: str
    checkpoint: Path
    task: str | None = None
    classes_file: Path | None = None


def _pt(name: str, module: str, model_type: str, relative: str, task: str | None = None) -> VisionModelConfig:
    return VisionModelConfig(name, module, model_type, VISION_ROOT / relative, task)


VISION_MODELS: dict[str, VisionModelConfig] = {
    "allergen": _pt("allergen", "allergen", "yolo_detection", "allergen/models/final/allergen30_yolo11n.pt", "detect"),
    "coffee": _pt("coffee", "coffee", "yolo_classification", "coffee/models/coffee_yolov8n.pt", "classify"),
    "farmer_seed": _pt("farmer_seed", "farmer_seed", "yolo_segmentation", "farmer_seed/runs/segment/oversampled_sequel_farmer_5ep/weights/best.pt", "segment"),
    "fruits": _pt("fruits", "fruits", "yolo_detection", "fruits/models/final/fruits_yolo11n.pt", "detect"),
    "grocery": _pt("grocery", "grocery", "yolo_detection", "grocery/models/final/grocery_detection_yolo11n.pt", "detect"),
    "grocery_segmentation": _pt("grocery_segmentation", "grocery", "yolo_segmentation", "grocery/models/final/indian_ingredients_yolo11n_seg.pt", "segment"),
    "indian_lentils": _pt("indian_lentils", "indian_lentils", "yolo_classification", "indian_lentils/models/indian_lentils_yolo11n.pt", "classify"),
    "chicken": _pt("chicken", "non-veg/chicken", "yolo_detection", "non-veg/chicken/models/final/chicken_yolov8n.pt", "detect"),
    "egg": _pt("egg", "non-veg/egg", "yolo_detection", "non-veg/egg/models/final/egg_yolo11n.pt", "detect"),
    "fish": _pt("fish", "non-veg/fish", "yolo_detection", "non-veg/fish/models/final/best.pt", "detect"),
    "mutton": _pt("mutton", "non-veg/mutton", "yolo_detection", "non-veg/mutton/models/final/mutton_yolov8n.pt", "detect"),
    "nuts": _pt("nuts", "nuts", "yolo_classification", "nuts/models/nuts_yolov8n.pt", "classify"),
    "green_tea": _pt("green_tea", "tea/Green_Tea", "yolo_detection", "tea/Green_Tea/models/green_tea_yolov8n.pt", "detect"),
    "red_tea": _pt("red_tea", "tea/Red_Tea", "yolo_detection", "tea/Red_Tea/models/red_tea_yolov8n.pt", "detect"),
    "vegetables": _pt("vegetables", "vegetables", "yolo_detection", "vegetables/models/final/vegetables_yolo11n.pt", "detect"),
    "spices": VisionModelConfig(
        "spices", "spices", "mobilenetv3_classification",
        VISION_ROOT / "spices/models/indian_spices_mobilenetv3.pth",
        classes_file=VISION_ROOT / "spices/models/indian_spices_classes.json",
    ),
}


MODEL_ALIASES = {"grocery_seg": "grocery_segmentation", "farmer": "farmer_seed", "spice": "spices"}


def resolve_model_name(name: str) -> str:
    normalized = name.strip().lower().replace("-", "_").replace(" ", "_")
    return MODEL_ALIASES.get(normalized, normalized)
