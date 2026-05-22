from pathlib import Path
import unittest


class StaticConfigTest(unittest.TestCase):
    def test_frontend_uses_declared_api_url_constant(self):
        html = Path("static/index.html").read_text(encoding="utf-8")

        self.assertNotIn("${API}/", html)
        self.assertNotIn("JSONBIN_ID", html)
        self.assertIn("window.location.origin", html)

    def test_frontend_has_visible_admin_login_button(self):
        html = Path("static/index.html").read_text(encoding="utf-8")

        self.assertIn('class="admin-login-btn"', html)
        self.assertNotIn('class="secret-btn"', html)

    def test_frontend_has_category_tab_management(self):
        html = Path("static/index.html").read_text(encoding="utf-8")

        self.assertIn('id="category-tabs"', html)
        self.assertIn('id="category-select"', html)
        self.assertIn('id="category-admin"', html)
        self.assertIn("loadCategories()", html)
        self.assertIn("addCategory()", html)
        self.assertIn("deleteCategory(", html)

    def test_frontend_has_edit_post_controls(self):
        html = Path("static/index.html").read_text(encoding="utf-8")

        self.assertIn("editPost(", html)
        self.assertIn("editingPostId", html)
        self.assertIn("PUT", html)

    def test_frontend_uses_blush_pink_theme(self):
        html = Path("static/index.html").read_text(encoding="utf-8")

        self.assertIn("--blush:", html)
        self.assertIn("--mauve:", html)
        self.assertIn("--glass:", html)
        self.assertIn("#fff7f9", html)
        self.assertNotIn("#d4836a", html)

    def test_frontend_has_linkedin_social_link(self):
        html = Path("static/index.html").read_text(encoding="utf-8")

        self.assertIn("https://www.linkedin.com/in/louisathuong/", html)
        self.assertIn("LinkedIn", html)


if __name__ == "__main__":
    unittest.main()
