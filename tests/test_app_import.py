import importlib
import unittest


class AppImportTest(unittest.TestCase):
    def test_main_module_exposes_fastapi_app(self):
        main = importlib.import_module("main")

        self.assertTrue(hasattr(main, "app"))


if __name__ == "__main__":
    unittest.main()
