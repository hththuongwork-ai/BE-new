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


if __name__ == "__main__":
    unittest.main()
