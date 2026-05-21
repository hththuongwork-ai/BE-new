import unittest

from schemas import PostCreate


class PostSchemaTest(unittest.TestCase):
    def test_post_create_accepts_frontend_embed_url_name(self):
        post = PostCreate(type="video", date="21/05/2026", embedUrl="https://example.test/embed")

        self.assertEqual(post.embed_url, "https://example.test/embed")


if __name__ == "__main__":
    unittest.main()
