from unittest import IsolatedAsyncioTestCase
from unittest import main
from unittest.mock import MagicMock
from unittest.mock import patch
from quart import Quart
from quart import session
from werkzeug.security import generate_password_hash

from openhti.authorize import authorize


class AuthorizeTestCase(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.app = Quart(__name__)
        self.app.secret_key = "testsecret"
        self.app.register_blueprint(authorize)
        self.client = self.app.test_client()

    async def test_login_get(self):
        """Test that GET /authorize/login returns the login template."""
        response = await self.client.get("/authorize/login")
        self.assertEqual(response.status_code, 200)
        html = await response.get_data(as_text=True)
        self.assertIn("login", html.lower())

    @patch("openhti.authorize.get_db")
    async def test_validate_invalid_password(self, mock_get_db):
        """Test that POST /authorize/login with an invalid password redirects back to login."""

        mock_db = MagicMock()
        mock_db.execute.return_value.fetchone.return_value = {
            "value": generate_password_hash("secret")
        }
        mock_get_db.return_value = mock_db
        data = {"password": "wrong"}
        response = await self.client.post("/authorize/login", data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers.get("Location"), "/authorize/login")

    @patch("openhti.authorize.get_db")
    async def test_validate_valid_password(self, mock_get_db):
        """Test that POST /authorize/login with a valid password sets session['unlocked']."""

        mock_db = MagicMock()
        mock_db.execute.return_value.fetchone.return_value = {
            "value": generate_password_hash("secret")
        }
        mock_get_db.return_value = mock_db
        data = {"password": "secret"}
        response = await self.client.post("/authorize/login", data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers.get("Location"), "/home")
        async with self.client.session_transaction() as sess:
            self.assertTrue(sess.get("unlocked"))

    async def test_logout(self):
        """Test that GET /authorize/logout clears the session and redirects to home."""

        async with self.client.session_transaction() as sess:
            sess["unlocked"] = True
        response = await self.client.get("/authorize/logout")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers.get("Location"), "/home")
        async with self.client.session_transaction() as sess:
            self.assertNotIn("unlocked", sess)


if __name__ == "__main__":
    main()
