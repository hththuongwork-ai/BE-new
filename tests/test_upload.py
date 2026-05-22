import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import main


class UploadApiTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(main.app)
        self.original_cloud = main.CLOUDINARY_CLOUD
        self.original_preset = main.CLOUDINARY_PRESET

    def tearDown(self):
        main.CLOUDINARY_CLOUD = self.original_cloud
        main.CLOUDINARY_PRESET = self.original_preset

    def test_upload_returns_clear_error_when_cloudinary_config_is_missing(self):
        main.CLOUDINARY_CLOUD = ""
        main.CLOUDINARY_PRESET = ""

        response = self.client.post(
            "/upload",
            files={"image": ("tiny.png", b"not-really-an-image", "image/png")},
        )

        self.assertEqual(response.status_code, 500)
        self.assertIn("Thiếu cấu hình Cloudinary", response.json()["detail"])

    def test_upload_includes_cloudinary_error_message(self):
        main.CLOUDINARY_CLOUD = "demo-cloud"
        main.CLOUDINARY_PRESET = "bad-preset"

        class FakeResponse:
            status_code = 400
            text = '{"error":{"message":"Upload preset not found"}}'

            def json(self):
                return {"error": {"message": "Upload preset not found"}}

        class FakeAsyncClient:
            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                return False

            async def post(self, *args, **kwargs):
                return FakeResponse()

        with patch("httpx.AsyncClient", FakeAsyncClient):
            response = self.client.post(
                "/upload",
                files={"image": ("tiny.png", b"not-really-an-image", "image/png")},
            )

        self.assertEqual(response.status_code, 502)
        self.assertIn("Upload preset not found", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
