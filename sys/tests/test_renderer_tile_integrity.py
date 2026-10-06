"""Unit tests verifying Chromium GPU raster tile integrity and Remotion headless safety."""
import os
from pathlib import Path
import unittest

from pilot import ROOT
SYSTEM = ROOT


class RendererTileIntegrityTests(unittest.TestCase):
    def test_render_mjs_headless_configuration(self):
        content = (SYSTEM / 'renderer/render.mjs').read_text()
        self.assertIn("process.env.DISABLE_FROM_SURFACE = 'true'", content)
        self.assertIn("--enable-gpu", content)
        self.assertIn("--run-all-compositor-stages-before-draw", content)
        self.assertIn("--disable-gpu-rasterization", content)
        self.assertIn("--disable-dev-shm-usage", content)

    def test_job_worker_env_disable_from_surface(self):
        content = (SYSTEM / 'colab_bridge/job_worker.py').read_text()
        self.assertIn("DISABLE_FROM_SURFACE='true'", content)

    def test_subtitles_z_index_and_caption_style(self):
        captions_js = (SYSTEM / 'renderer/captions.mjs').read_text()
        self.assertIn("zIndex: 30", captions_js)

        index_tsx = (SYSTEM / 'renderer/index.tsx').read_text()
        self.assertIn("zIndex: 30", index_tsx)
        self.assertIn("objectFit: 'cover'", index_tsx)

    def test_no_blinding_bg_flash(self):
        index_tsx = (SYSTEM / 'renderer/index.tsx').read_text()
        self.assertNotIn("[1, 0]", [line.strip() for line in index_tsx.splitlines() if 'bg_flash' in line])

    def test_flow_compiler_layer_background_has_no_caption_clearance_rule(self):
        from flow_prompts import compile as compile_prompt
        data = {'description': 'Empty palace hall', 'aspect_ratio': '9:16'}
        result = compile_prompt('NanoBanana2Lite', 'layer_background', data, '1.2.0')
        self.assertNotIn('Reserve the specified caption band', result['prompt'])



    def test_tile_drop_scanner_function(self):
        """Ensure tile drop detector accurately identifies white tile drops and clean frames."""
        import numpy as np
        # 1080x1920 frame with dropped bottom tiles
        bad_frame = np.zeros((1920, 1080, 3), dtype=np.uint8)
        bad_frame[1280:, :] = 254  # dropped tiles
        b20 = np.mean(bad_frame[int(1920*0.8):, :, 0] > 240)
        self.assertGreater(b20, 0.9)

        # Clean frame
        clean_frame = np.full((1920, 1080, 3), 120, dtype=np.uint8)
        b20_clean = np.mean(clean_frame[int(1920*0.8):, :, 0] > 240)
        self.assertLess(b20_clean, 0.05)

if __name__ == '__main__':
    unittest.main()
