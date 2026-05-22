from pathlib import Path
import unittest


class StaticConfigTest(unittest.TestCase):
    def test_frontend_uses_declared_api_url_constant(self):
        html = Path("static/index.html").read_text(encoding="utf-8")

        self.assertNotIn("${API}/", html)
        self.assertNotIn("JSONBIN_ID", html)
        self.assertNotIn("CDN_PRESET", html)
        self.assertNotIn("QR_IMAGE_URL", html)
        self.assertIn("window.location.origin", html)
        self.assertIn('src="/qr-image"', html)

    def test_frontend_hides_admin_login_until_admin_entry_url(self):
        html = Path("static/index.html").read_text(encoding="utf-8")

        self.assertIn('class="admin-login-btn"', html)
        self.assertNotIn('class="secret-btn"', html)
        self.assertIn(".admin-login-btn{display:none;", html)
        self.assertIn(".show-admin-login .admin-login-btn", html)
        self.assertIn("adminEntryEnabled", html)
        self.assertIn("get('admin')", html)
        self.assertIn("=== '1'", html)

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

    def test_mobile_feed_has_padding_and_no_post_chips(self):
        html = Path("static/index.html").read_text(encoding="utf-8")

        self.assertIn("@media (max-width: 640px)", html)
        self.assertIn(".mobile-safe", html)
        self.assertNotIn("type-chip", html)
        self.assertNotIn("typeLabel(", html)
        self.assertNotIn("categoryName(", html)

    def test_photo_cards_have_inner_padding(self):
        html = Path("static/index.html").read_text(encoding="utf-8")

        self.assertIn(".gallery-frame", html)
        self.assertIn("padding:14px 20px 20px", html)


if __name__ == "__main__":
    unittest.main()
