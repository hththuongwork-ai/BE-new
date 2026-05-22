import time
import unittest

from fastapi.testclient import TestClient

from main import app


class CategoryApiTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_default_categories_are_available(self):
        response = self.client.get("/categories")

        self.assertEqual(response.status_code, 200)
        slugs = {category["slug"] for category in response.json()}
        self.assertTrue({"work", "daily-life", "pet", "travel"}.issubset(slugs))

    def test_can_create_and_delete_custom_category(self):
        slug = f"custom-{time.time_ns()}"

        create_response = self.client.post("/categories", json={"name": "Custom Tab", "slug": slug})
        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(create_response.json()["slug"], slug)

        list_response = self.client.get("/categories")
        self.assertIn(slug, {category["slug"] for category in list_response.json()})

        delete_response = self.client.delete(f"/categories/{slug}")
        self.assertEqual(delete_response.status_code, 200)

    def test_posts_can_be_filtered_by_category(self):
        slug = f"post-cat-{time.time_ns()}"
        self.client.post("/categories", json={"name": "Post Category", "slug": slug})

        create_response = self.client.post(
            "/posts",
            json={
                "type": "text",
                "title": "Category test",
                "body": "Only this tab should show it",
                "date": "22/05/2026",
                "category": slug,
            },
        )
        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(create_response.json()["category"], slug)

        filtered_response = self.client.get(f"/posts?category={slug}")
        self.assertEqual(filtered_response.status_code, 200)
        self.assertTrue(all(post["category"] == slug for post in filtered_response.json()))


if __name__ == "__main__":
    unittest.main()
