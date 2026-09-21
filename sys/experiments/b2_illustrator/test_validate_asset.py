import tempfile
import unittest
from pathlib import Path
from PIL import Image
from validate_asset import validate_asset

class AssetTests(unittest.TestCase):
    def test_bytes_override_misleading_extension(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / 'wrong.png'
            Image.new('RGB', (160, 90)).save(file, format='JPEG')
            result = validate_asset(file, '16:9')
            self.assertEqual(result['extension'], '.jpg')
            self.assertEqual(result['visualReview'], 'pending')
            with self.assertRaises(ValueError):
                validate_asset(file, '16:9', 'image/png')
            with self.assertRaises(ValueError):
                validate_asset(file, '9:16')
    def test_html_disguised_as_image_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / 'error.png'
            file.write_text('<html>Login required</html>')
            with self.assertRaises(OSError):
                validate_asset(file, '16:9')

if __name__ == '__main__':
    unittest.main()
