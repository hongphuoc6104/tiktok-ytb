"""Unit tests for deterministic flood-fill matte and sticker outline generator."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_DIR = ROOT.parent
for p in (str(REPO_DIR), str(ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np
from PIL import Image, ImageDraw

from tools.matte_sticker import floodfill_matte, make_sticker_outline, process_image


class MatteStickerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_stickman_head_synthetic(self, size=(200, 200)) -> Image.Image:
        """Create synthetic stickman head: pure white background with black circle enclosing white interior."""
        im = Image.new("RGB", size, (255, 255, 255))
        draw = ImageDraw.Draw(im)
        # Draw black outline circle with white interior
        bbox = (50, 50, 150, 150)
        draw.ellipse(bbox, fill=(255, 255, 255), outline=(0, 0, 0), width=6)
        # Add simple dot eyes
        draw.ellipse((80, 85, 88, 93), fill=(0, 0, 0))
        draw.ellipse((112, 85, 120, 93), fill=(0, 0, 0))
        return im

    def test_floodfill_preserves_interior_white(self):
        im = self._create_stickman_head_synthetic()
        matted = floodfill_matte(im)

        self.assertEqual(matted.mode, "RGBA")
        arr = np.array(matted)

        # 1. Outer background corners must be transparent (alpha == 0)
        self.assertEqual(arr[10, 10, 3], 0)
        self.assertEqual(arr[5, 190, 3], 0)

        # 2. Interior white region (center of head) must be 100% opaque (alpha == 255)
        # u2net/rembg would fail this by hollowing out the white head
        self.assertEqual(arr[100, 100, 3], 255)
        self.assertGreater(arr[100, 100, :3].min(), 240)

        # 3. Black stroke boundary must be opaque
        # Top of head circle around y=50, x=100
        self.assertEqual(arr[52, 100, 3], 255)
        self.assertLess(arr[52, 100, :3].max(), 50)

    def test_make_sticker_outline(self):
        im = self._create_stickman_head_synthetic()
        matted = floodfill_matte(im)
        sticker = make_sticker_outline(matted, border=10, blur=1.0)

        self.assertEqual(sticker.mode, "RGBA")
        # Check that sticker has expanded beyond original tight bbox
        alpha = sticker.getchannel("A")
        bbox = alpha.getbbox()
        self.assertIsNotNone(bbox)
        # Sticker dimensions must be non-empty and reasonably sized
        self.assertGreater(sticker.width, 100)
        self.assertGreater(sticker.height, 100)

    def test_cli_execution(self):
        src_path = self.test_dir / "test_stickman.jpg"
        dst_path = self.test_dir / "out_sticker.png"
        im = self._create_stickman_head_synthetic()
        im.save(src_path, "JPEG")

        python_bin = sys.executable if sys.executable else str(ROOT / ".venv/bin/python")
        cmd = [
            python_bin,
            str(ROOT / "tools/matte_sticker.py"),
            "--input",
            str(src_path),
            "--output",
            str(dst_path),
            "--sticker",
            "--border",
            "8",
        ]
        res = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"CLI error: {res.stderr}")
        self.assertTrue(dst_path.exists())

        out_im = Image.open(dst_path)
        self.assertEqual(out_im.mode, "RGBA")
        arr = np.array(out_im)
        # Confirm interior center is preserved
        center_y, center_x = arr.shape[0] // 2, arr.shape[1] // 2
        self.assertEqual(arr[center_y, center_x, 3], 255)


if __name__ == "__main__":
    unittest.main()
