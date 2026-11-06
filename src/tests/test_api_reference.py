import importlib.util
import sys
from pathlib import Path
from unittest import TestCase

ROOT = Path(__file__).resolve().parents[2]


def load_generator():
    spec = importlib.util.spec_from_file_location("generate_api", ROOT / "scripts" / "generate_api.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class APIReferenceTestCase(TestCase):

    def test_api_md_is_up_to_date(self):
        """src/tasi/API.md must match the code. Regenerate with
        ``uv run --all-extras python scripts/generate_api.py``."""
        generator = load_generator()

        self.assertEqual(
            generator.OUTPUT.read_text(),
            generator.render(),
            "src/tasi/API.md is outdated, run: uv run --all-extras python scripts/generate_api.py",
        )

    def test_package_is_typed(self):
        self.assertTrue((ROOT / "src" / "tasi" / "py.typed").exists())
