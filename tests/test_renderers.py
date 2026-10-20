import importlib.util
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SPRITES = load_module(
    "sprite_renderer",
    ROOT
    / "plugins"
    / "sprite-workshop"
    / "skills"
    / "sprite-workshop"
    / "scripts"
    / "render.py",
)
OPS = load_module(
    "ops_renderer",
    ROOT
    / "plugins"
    / "ops-characters"
    / "skills"
    / "ops-characters"
    / "scripts"
    / "render.py",
)


class SpriteRendererTests(unittest.TestCase):
    def test_svg_is_deterministic_and_valid_xml(self):
        first = SPRITES.render_sprite_sheet(
            "Service Bot", ["idle", "repair"], "svg"
        )
        second = SPRITES.render_sprite_sheet(
            "Service Bot", ["idle", "repair"], "svg"
        )

        self.assertEqual(first, second)
        ET.fromstring(first)
        self.assertIn("Service Bot sprite sheet", first)

    def test_unknown_pose_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported pose"):
            SPRITES.render_sprite_sheet("Service Bot", ["flying"], "markdown")


class OpsRendererTests(unittest.TestCase):
    def test_markdown_preserves_state_metrics_and_uncertainty(self):
        output = OPS.render_ops_card(
            service="checkout-api",
            state="degraded",
            metrics={"Error rate": "8.4%", "P95 latency": "1.8 s"},
            suspected_cause="Connection-pool exhaustion",
            evidence=["Alert 42"],
            output_format="markdown",
        )

        self.assertIn("checkout-api | DEGRADED", output)
        self.assertIn("Error rate: 8.4%", output)
        self.assertIn(
            "Suspected cause: Connection-pool exhaustion",
            output,
        )
        self.assertIn("Evidence: Alert 42", output)

    def test_svg_is_deterministic_and_valid_xml(self):
        first = OPS.render_ops_card("payments", "healthy", output_format="svg")
        second = OPS.render_ops_card("payments", "healthy", output_format="svg")

        self.assertEqual(first, second)
        ET.fromstring(first)
        self.assertIn("payments operational status", first)

    def test_unknown_state_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported state"):
            OPS.render_ops_card("payments", "offline")


if __name__ == "__main__":
    unittest.main()
