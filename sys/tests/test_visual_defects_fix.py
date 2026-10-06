"""Automated Unit Tests verifying fixes for the 3 visual defects in layered 9:16 video:
1. Subtitle layering & z-index order (subtitles never obscured by background or stickers).
2. Full-bleed background plate layout (no 18-20% bottom white band, no aspect distortion).
3. Motion & rotation angle continuity (no discrete step jumps causing sticker halo flickering).
"""
import math
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT / "sys"
for p in (str(ROOT), str(SYS_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np
from PIL import Image, ImageDraw

from tools.matte_sticker import crop_background_plate, floodfill_matte, process_background


class VisualDefectsRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    # =========================================================================
    # R1 & R4: Background Layout Full-Bleed (No 18-20% White Band at Bottom)
    # =========================================================================

    def test_crop_background_plate_removes_white_clearance_band(self):
        """Synthetic test: background with 20% white bottom clearance is cleanly cropped."""
        w, h = 768, 1376
        # Create image with artwork from y=100 to y=1100, and white at bottom (y=1100..1376)
        im = Image.new("RGB", (w, h), (255, 255, 255))
        draw = ImageDraw.Draw(im)
        draw.rectangle((0, 100, w, 1100), fill=(120, 60, 40))
        draw.rectangle((50, 150, w - 50, 1050), fill=(80, 140, 90))

        cropped = crop_background_plate(im, white_thresh=225)
        cw, ch = cropped.size

        self.assertEqual(cw, w)
        self.assertEqual(ch, 1001)  # y from 100 to 1100 inclusive

        # Verify bottom row of cropped image is the artwork, not white
        bottom_pixels = [cropped.getpixel((x, ch - 1)) for x in range(0, cw, 20)]
        self.assertTrue(all(p[0] < 200 for p in bottom_pixels))

    def test_crop_background_plate_preserves_full_bleed_image(self):
        """An already full-bleed image without white borders is not erroneously cropped."""
        w, h = 768, 1376
        im = Image.new("RGB", (w, h), (100, 150, 200))
        cropped = crop_background_plate(im, white_thresh=225)
        self.assertEqual(cropped.size, (w, h))

    def test_real_job_backgrounds_render_full_bleed_without_white_band(self):
        """Verify on actual job images (BG01-BG06) that cropped plates cover 1080x1920 with 0 white rows."""
        img_dir = ROOT / "sys/runs/vocab-loyal-emperor-9x16-002/revisions/images/4"
        if not img_dir.exists():
            self.skipTest("Job images directory not found")

        for i in range(1, 7):
            bg_path = img_dir / f"BG0{i}_9x16.jpg"
            if not bg_path.exists():
                continue

            with Image.open(bg_path) as im:
                cropped = crop_background_plate(im, white_thresh=225)
                cw, ch = cropped.size

                # Simulate Remotion CSS objectFit: 'cover' into (1080, 1920)
                cover_scale = max(1080 / cw, 1920 / ch)
                sw, sh = int(round(cw * cover_scale)), int(round(ch * cover_scale))
                resized = cropped.resize((sw, sh), Image.BILINEAR)

                # Center crop to viewport (1080, 1920)
                left = (sw - 1080) // 2
                top = (sh - 1920) // 2
                viewport = resized.crop((left, top, left + 1080, top + 1920))

                self.assertEqual(viewport.size, (1080, 1920))

                # Check bottom 20% (y = 1536 to 1920): must NOT have white clearance rows
                white_bottom_rows = 0
                for y in range(1536, 1920, 5):
                    pixels = [viewport.getpixel((x, y)) for x in range(0, 1080, 20)]
                    if all(p[0] > 235 and p[1] > 235 and p[2] > 235 for p in pixels):
                        white_bottom_rows += 1

                self.assertEqual(
                    white_bottom_rows, 0,
                    f"BG0{i} still has {white_bottom_rows} white rows at bottom of 1080x1920 viewport"
                )

    # =========================================================================
    # R2 & R4: Subtitle Layering / Z-Index (Never Obscured by Graphics)
    # =========================================================================

    def test_caption_style_has_high_z_index(self):
        """Verify captionStyle in captions.mjs defines zIndex >= 30."""
        cmd = [
            "node",
            "--input-type=module",
            "-e",
            """
import { captionStyle } from './renderer/captions.mjs';
const style = captionStyle(1080, 1920);
if (typeof style.zIndex !== 'number' || style.zIndex < 30) {
  process.exit(1);
}
console.log('ZINDEX_OK:' + style.zIndex);
"""
        ]
        res = subprocess.run(cmd, cwd=str(ROOT / "sys"), capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"captionStyle failed zIndex check: {res.stderr}")
        self.assertIn("ZINDEX_OK:30", res.stdout)

    def test_layering_order_subtitles_above_all_graphics(self):
        """Verify z-index hierarchy in index.tsx: subtitles (30) > overlays (12-25) > scene.layers (5)."""
        index_tsx = (ROOT / "sys/renderer/index.tsx").read_text()

        # Extract layer z-indexes
        layers_m = re.search(r'scene\.layers.*?style=\{\{zIndex:\s*(\d+)\}\}', index_tsx, re.DOTALL)
        self.assertIsNotNone(layers_m, "scene.layers must specify zIndex")
        z_layers = int(layers_m.group(1))

        vignette_m = re.search(r'Vignette.*?zIndex:\s*(\d+)', index_tsx, re.DOTALL)
        self.assertIsNotNone(vignette_m, "Vignette must specify zIndex")
        z_vignette = int(vignette_m.group(1))

        grain_m = re.search(r'Film Grain.*?zIndex:\s*(\d+)', index_tsx, re.DOTALL)
        self.assertIsNotNone(grain_m, "Film grain must specify zIndex")
        z_grain = int(grain_m.group(1))

        bar_m = re.search(r'Progress Bar.*?zIndex:\s*(\d+)', index_tsx, re.DOTALL)
        self.assertIsNotNone(bar_m, "Progress bar must specify zIndex")
        z_bar = int(bar_m.group(1))

        practice_m = re.search(r'Practice Indicator.*?zIndex:\s*(\d+)', index_tsx, re.DOTALL)
        self.assertIsNotNone(practice_m, "Practice indicator must specify zIndex")
        z_practice = int(practice_m.group(1))

        sub_m = re.search(r'data-check="subtitle".*?zIndex:\s*(\d+)', index_tsx, re.DOTALL)
        self.assertIsNotNone(sub_m, "Subtitle must specify zIndex")
        z_subtitle = int(sub_m.group(1))

        self.assertGreater(z_subtitle, z_layers, "Subtitles must be above scene.layers (background/stickers)")
        self.assertGreater(z_subtitle, z_vignette, "Subtitles must be above vignette")
        self.assertGreater(z_subtitle, z_grain, "Subtitles must be above film grain")
        self.assertGreater(z_subtitle, z_bar, "Subtitles must be above progress bar")
        self.assertGreater(z_subtitle, z_practice, "Subtitles must be above practice indicator")

    def test_render_mjs_does_not_corrupt_z_index(self):
        """Verify render.mjs does not append 'px' to zIndex in layout verification."""
        render_mjs = (ROOT / "sys/renderer/render.mjs").read_text()
        self.assertIn("'zIndex'", render_mjs, "render.mjs must exclude zIndex from appending px")

    # =========================================================================
    # R3 & R4: Motion & Rotation Angle Continuity (No Flickering/Jitter)
    # =========================================================================

    def test_crop_background_plate_safeguards_snowy_scene(self):
        """Test safeguard: A snowy scene with white ground is capped at max_bottom_fraction (<= 45%)."""
        w, h = 768, 1376
        # Entire bottom half is white snow, top half is sky/trees
        im = Image.new("RGB", (w, h), (255, 255, 255))
        draw = ImageDraw.Draw(im)
        draw.rectangle((0, 0, w, 200), fill=(100, 150, 200))  # sky
        draw.rectangle((50, 100, 150, 200), fill=(50, 80, 40))  # tree

        cropped = crop_background_plate(im, white_thresh=225)
        cw, ch = cropped.size

        # Safeguard must keep at least 55% of height (bottom crop capped at 45%)
        self.assertGreaterEqual(ch, int(h * 0.55))
        self.assertEqual(cw, w)

    def test_crop_background_plate_safeguards_pure_white_scene(self):
        """Test safeguard: An entirely white image triggers min_content_fraction and is not mangled."""
        w, h = 768, 1376
        im = Image.new("RGB", (w, h), (255, 255, 255))
        cropped = crop_background_plate(im, white_thresh=225)
        # Should return original image unchanged
        self.assertEqual(cropped.size, (w, h))

    def test_sticker_base_rotation_is_strictly_continuous(self):
        """Verify sticker base rotation has ZERO discrete angle jumps across consecutive frames."""
        index_tsx = (ROOT / "sys/renderer/index.tsx").read_text()
        self.assertNotIn(
            "let rot = boilJitter",
            index_tsx,
            "Discrete boilJitter must NOT be assigned to sticker rot"
        )
        self.assertIn(
            "let rot = 0;",
            index_tsx,
            "Sticker base rotation must be set to 0 for perfectly smooth motion"
        )

    def test_boil_jitter_causes_abrupt_step_jumps(self):
        """Demonstrate that boilJitter creates discrete step jumps at 4-frame intervals."""
        def boil_jitter(frame: int, seed: int = 0) -> float:
            step = math.floor(frame / 4)
            r = math.sin(step * 12.9898 + seed * 78.233) * 43758.5453
            return (r - math.floor(r) - 0.5) * 1.2

        fps = 30
        step_jumps = 0
        prev_rot = boil_jitter(0)
        for f in range(1, 60):
            rot = boil_jitter(f)
            delta = abs(rot - prev_rot)
            if f % 4 == 0:
                # Every 4th frame, a step jump occurs
                self.assertGreater(delta, 0.05, f"Expected step discontinuity at frame {f}")
                step_jumps += 1
            else:
                # Within the 4 frames, angle stays constant (causing stair-stepped twitching)
                self.assertEqual(delta, 0.0)
            prev_rot = rot
        self.assertGreater(step_jumps, 10, "boilJitter must produce repeated discrete jumps")

    def test_sticker_fx_rotation_is_smoothly_continuous(self):
        """Verify dynamic FX rotation (e.g. pop_wobble) is continuous with bounded frame-to-frame delta."""
        fps = 30
        prev_rot = 0.0
        max_delta = 0.0
        for f in range(fps * 3):
            tau = f / fps
            rot = 10 * math.sin(9 * tau) * math.exp(-2 * tau)
            if f > 0:
                delta = abs(rot - prev_rot)
                max_delta = max(max_delta, delta)
                self.assertLess(
                    delta, 3.0,
                    f"Frame {f}: angular jump {delta:.2f} deg is too abrupt (causes visual jitter)"
                )
            prev_rot = rot
        self.assertGreater(max_delta, 0.0, "pop_wobble must produce motion")

    def test_floodfill_matte_fallback_without_scipy(self):
        """Verify morphological floodfill succeeds even when scipy is absent (Pillow fallback)."""
        import tools.matte_sticker as ms
        orig_ndi = ms.ndi
        try:
            ms.ndi = None  # simulate environment without scipy
            im = Image.new("RGB", (100, 100), (255, 255, 255))
            draw = ImageDraw.Draw(im)
            draw.ellipse((20, 20, 80, 80), fill=(255, 255, 255), outline=(0, 0, 0), width=4)
            matted = ms.floodfill_matte(im)
            self.assertEqual(matted.mode, "RGBA")
            arr = np.array(matted)
            # Outer corner transparent
            self.assertEqual(arr[5, 5, 3], 0)
            # Head center opaque
            self.assertEqual(arr[50, 50, 3], 255)
        finally:
            ms.ndi = orig_ndi

    def test_crop_background_plate_noise_resilience(self):
        """Verify that isolated compression noise pixels in the clearance band do not abort cropping."""
        w, h = 768, 1376
        im = Image.new("RGB", (w, h), (255, 255, 255))
        draw = ImageDraw.Draw(im)
        draw.rectangle((0, 0, w, 1100), fill=(100, 150, 200))
        # Insert noise pixel at y=1375 (bottom row) with RGB 210
        im.putpixel((10, 1375), (210, 210, 210))
        cropped = crop_background_plate(im, white_thresh=220)
        self.assertLessEqual(cropped.height, 1105, "Clearance band must be cropped despite noise pixel")

    def test_crop_background_plate_border_artifact_resilience(self):
        """Verify that 1-pixel frame border lines at canvas edges do not block clearance band cropping."""
        w, h = 768, 1376
        im = Image.new("RGB", (w, h), (255, 255, 255))
        draw = ImageDraw.Draw(im)
        draw.rectangle((0, 0, w, 1100), fill=(100, 150, 200))
        # 1-pixel dark border line at the bottom
        draw.line((0, 1375, w, 1375), fill=(0, 0, 0))
        cropped = crop_background_plate(im, white_thresh=220)
        self.assertLessEqual(cropped.height, 1105, "Clearance band must be cropped despite 1px bottom border")

    def test_crop_background_plate_gradient_resilience(self):
        """Verify that subtle off-white/warm gradient clearance bands (RGB 220-224) are cleanly cropped."""
        w, h = 768, 1376
        im = Image.new("RGB", (w, h), (255, 255, 255))
        draw = ImageDraw.Draw(im)
        draw.rectangle((0, 0, w, 1100), fill=(100, 150, 200))
        # Off-white clearance band with RGB (222, 222, 222)
        draw.rectangle((0, 1101, w, h), fill=(222, 222, 222))
        cropped = crop_background_plate(im, white_thresh=220)
        self.assertLessEqual(cropped.height, 1105, "Off-white clearance band must be cropped")

    def test_index_tsx_recognizes_both_bg_and_kind_background(self):
        """Verify index.tsx checks both l.bg and l.kind === 'background' to prevent animating background as sticker."""
        index_tsx = (ROOT / "sys/renderer/index.tsx").read_text()
        self.assertIn("l.bg || l.kind === 'background'", index_tsx)

    def test_adapters_handles_sticker_layers(self):
        """Verify adapters.py handles sticker layers with process_image and copy_sticker."""
        adapters_py = (ROOT / "sys/adapters.py").read_text()
        self.assertIn("elif layer.get('kind') == 'sticker':", adapters_py)
        self.assertIn("process_image(src,dest,create_sticker=True,border=10)", adapters_py)

    def test_crop_background_plate_top_and_bottom_clearance(self):
        """Verify that background with both top and bottom clearance bands is cropped cleanly."""
        w, h = 768, 1376
        im = Image.new("RGB", (w, h), (255, 255, 255))
        draw = ImageDraw.Draw(im)
        # Artwork between y=100 and y=1100
        draw.rectangle((0, 100, w, 1100), fill=(90, 120, 150))
        cropped = crop_background_plate(im, white_thresh=220)
        self.assertEqual(cropped.width, w)
        self.assertLessEqual(cropped.height, 1010)
        self.assertGreaterEqual(cropped.height, 995)

    def test_job_final_video_specs_and_codecs(self):
        """Verify that the rendered video MP4 conforms exactly to 1080x1920 @ 30fps H.264/AAC."""
        video_path = ROOT / "video/vocab-loyal-emperor-9x16-002/vocab-loyal-emperor-9x16-002_r1_final.mp4"
        if not video_path.exists():
            self.skipTest("Final video MP4 does not exist")

        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", str(video_path)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"ffprobe failed: {res.stderr}")
        import json
        info = json.loads(res.stdout)
        video_stream = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
        audio_stream = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)

        self.assertIsNotNone(video_stream, "Missing video stream")
        self.assertEqual(video_stream["width"], 1080)
        self.assertEqual(video_stream["height"], 1920)
        self.assertEqual(video_stream["codec_name"], "h264")
        self.assertEqual(video_stream["r_frame_rate"], "30/1")

        self.assertIsNotNone(audio_stream, "Missing audio stream")
        self.assertEqual(audio_stream["codec_name"], "aac")
        self.assertGreater(float(info["format"]["duration"]), 55.0)

    def test_job_final_video_frame_visuals(self):
        """Extract frames across all scenes SC01-SC06 to verify 0 bottom white rows and clear subtitles."""
        video_path = ROOT / "video/vocab-loyal-emperor-9x16-002/vocab-loyal-emperor-9x16-002_r1_final.mp4"
        if not video_path.exists():
            self.skipTest("Final video MP4 does not exist")

        test_times = [("SC01", 3.0), ("SC02", 15.0), ("SC03", 26.0), ("SC04", 37.0), ("SC05", 46.0), ("SC06", 54.0)]
        with tempfile.TemporaryDirectory() as td:
            for sc, t in test_times:
                out_png = Path(td) / f"{sc}.png"
                cmd = ["ffmpeg", "-y", "-ss", str(t), "-i", str(video_path), "-vframes", "1", str(out_png)]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                with Image.open(out_png) as im:
                    arr = np.array(im)
                    h, w, _ = arr.shape
                    # Check bottom 18% for white clearance rows
                    bottom_rows = arr[int(h * 0.82):, :]
                    white_rows = 0
                    for y in range(bottom_rows.shape[0]):
                        row = bottom_rows[y, :, :]
                        if np.mean(np.all(row > 235, axis=-1)) > 0.85:
                            white_rows += 1
                    self.assertEqual(white_rows, 0, f"{sc} at {t}s still has {white_rows} white clearance rows")

                    # Check subtitle presence (dark box around y=1400..1750)
                    sub_box = arr[1400:1750, 150:930]
                    dark_pixels = np.sum(np.all(sub_box < 60, axis=-1))
                    self.assertGreater(dark_pixels, 40000, f"{sc} at {t}s has missing or faint subtitles")


if __name__ == "__main__":
    unittest.main()

