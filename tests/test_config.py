from pathlib import Path
import unittest


class ConfigTest(unittest.TestCase):
    def test_runtime_config_is_not_hardcoded_in_main(self):
        source = Path("main.py").read_text(encoding="utf-8")

        self.assertIn('load_dotenv(dotenv_path=Path(__file__).parent / ".env")', source)
        self.assertIn('ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD") or os.getenv("ADMIN_PASS", "")', source)
        self.assertIn('CLOUDINARY_CLOUD = os.getenv("CLOUDINARY_CLOUD", "")', source)
        self.assertIn('CLOUDINARY_PRESET = os.getenv("CLOUDINARY_PRESET", "")', source)
        self.assertIn('QR_IMAGE_URL = os.getenv("QR_IMAGE_URL", "")', source)


if __name__ == "__main__":
    unittest.main()
