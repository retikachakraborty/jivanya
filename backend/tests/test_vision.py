import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from app.services.vision_service import VisionService
from app.services.vision_config import VISION_MODELS


class VisionRoutingTests(unittest.TestCase):
    def test_supported_foods_are_derived_from_existing_metadata(self):
        foods = VisionService().supported_classes()

        self.assertIn("carrot", {food.casefold() for food in foods})
        self.assertIn("tomato", {food.casefold() for food in foods})
        self.assertGreater(len(foods), 20)
        self.assertEqual(len(foods), len({food.casefold() for food in foods}))

    def test_auto_routing_selects_highest_confident_existing_model_result(self):
        service = VisionService()
        configs = [
            SimpleNamespace(name="fruits", module="fruits", model_type="yolo_detection"),
            SimpleNamespace(name="vegetables", module="vegetables", model_type="yolo_detection"),
        ]
        service.configs = Mock(return_value=configs)
        service.checkpoint_available = Mock(return_value=True)
        service.predict = Mock(side_effect=lambda name, _image: {
            "fruits": {"predictions": [{"label": "apple", "confidence": 0.89}]},
            "vegetables": {"predictions": [{"label": "carrot", "confidence": 0.71}]},
        }[name])

        result = service.predict_auto(b"image")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["model"], "fruits")
        self.assertEqual(result["predictions"][0]["label"], "apple")
        self.assertEqual(result["predictions"][0]["confidence"], 0.89)
        self.assertEqual(service.predict.call_count, 2)

    def test_auto_routing_does_not_fabricate_low_confidence_detection(self):
        service = VisionService()
        config = SimpleNamespace(name="vegetables", module="vegetables", model_type="yolo_detection")
        service.configs = Mock(return_value=[config])
        service.checkpoint_available = Mock(return_value=True)
        service.predict = Mock(return_value={"predictions": [{"label": "unknown", "confidence": 0.2}]})

        result = service.predict_auto(b"image")

        self.assertEqual(result["status"], "no_detection")
        self.assertEqual(result["predictions"], [])

    def test_auto_routing_rejects_confident_unresolvable_labels(self):
        service = VisionService()
        configs = [
            SimpleNamespace(name="vegetables", module="vegetables", model_type="yolo_detection"),
            SimpleNamespace(name="coffee", module="coffee", model_type="yolo_classification"),
        ]
        service.configs = Mock(return_value=configs)
        service.checkpoint_available = Mock(return_value=True)
        service.predict = Mock(side_effect=lambda name, _image: {
            "vegetables": {"predictions": [{"label": "light", "confidence": 0.99}]},
            "coffee": {"predictions": [{"label": "carrot", "confidence": 0.89}]},
        }[name])

        result = service.predict_auto(
            b"image",
            resolve_ingredient=lambda label: "carrot" if label == "carrot" else None,
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["predictions"][0]["label"], "carrot")
        self.assertEqual(result["predictions"][0]["canonical"], "carrot")

    def test_auto_routing_keeps_all_available_routes_reachable(self):
        service = VisionService()
        configs = list(VISION_MODELS.values())
        service.configs = Mock(return_value=configs)
        service.checkpoint_available = Mock(return_value=True)
        service.predict = Mock(side_effect=lambda name, _image: {
            "model": name,
            "predictions": [{"label": "carrot", "confidence": 0.81}],
        })

        result = service.predict_auto(b"image", resolve_ingredient=lambda _label: "carrot")

        self.assertEqual(result["status"], "success")
        self.assertEqual(service.predict.call_count, len(configs))
        self.assertEqual({call.args[0] for call in service.predict.call_args_list}, set(VISION_MODELS))

    def test_selected_model_uses_canonical_gate(self):
        service = VisionService()
        rejected = service.validate_selected_predictions(
            "coffee",
            {"model": "coffee", "model_type": "yolo_classification", "predictions": [
                {"label": "Light", "confidence": 0.99},
            ]},
            resolve_ingredient=lambda _label: None,
        )
        self.assertEqual(rejected["status"], "no_detection")
        self.assertEqual(rejected["predictions"], [])

        accepted = service.validate_selected_predictions(
            "vegetables",
            {"model": "vegetables", "model_type": "yolo_detection", "status": "success", "predictions": [
                {"label": "carrot", "confidence": 0.89},
            ]},
            resolve_ingredient=lambda label: "carrot" if label == "carrot" else None,
        )
        self.assertEqual(accepted["status"], "success")
        self.assertEqual(accepted["predictions"][0]["canonical"], "carrot")

    def test_model_cache_is_bounded_and_evicts_least_recently_used(self):
        service = VisionService()
        service.model_cache_size = 2
        service.checkpoint_available = Mock(return_value=True)
        service._load_spice_model = Mock(side_effect=lambda config: {"name": config.name})
        configs = [SimpleNamespace(name=name, model_type="mobilenetv3_classification", checkpoint="checkpoint") for name in ("fruits", "vegetables", "spices")]

        service._load(configs[0])
        service._load(configs[1])
        service._load(configs[0])
        service._load(configs[2])

        self.assertEqual(list(service._models), ["fruits", "spices"])
        self.assertFalse(service.is_loaded("vegetables"))
        self.assertLessEqual(len(service._models), 2)


if __name__ == "__main__":
    unittest.main()
