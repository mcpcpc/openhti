from tempfile import NamedTemporaryFile
from unittest import IsolatedAsyncioTestCase
from unittest import main
from unittest.mock import MagicMock
from unittest.mock import patch

from werkzeug.security import generate_password_hash

from openhti import create_app


class AuthorizeTestCase(IsolatedAsyncioTestCase):
    def setUp(self):
        self.db = NamedTemporaryFile()
        self.app = create_app({"TESTING": True, "DATABASE": self.db.name})
        self.app.test_cli_runner().invoke(args=["init-db"])
        self.client = self.app.test_client()

    def tearDown(self):
        self.db.close()

    async def test_login_get(self):
        """Test that GET /authorize/login returns the login template."""
        response = await self.client.get("/authorize/login")
        self.assertEqual(response.status_code, 200)
        html = await response.get_data(as_text=True)
        self.assertIn("login", html.lower())

    @patch("openhti.authorize.get_db")
    async def test_validate_missing_password(self, mock_get_db):
        """Test that POST /authorize/login with an missing password redirects back to login."""

        response = await self.client.post(
            "/authorize/login",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        html = await response.get_data(as_text=True)
        self.assertIn("Missing password.", html)
        async with self.client.session_transaction() as sess:
            self.assertNotIn("unlocked", sess)

    @patch("openhti.authorize.get_db")
    async def test_validate_invalid_password(self, mock_get_db):
        """Test that POST /authorize/login with an invalid password redirects back to login."""

        mock_db = MagicMock()
        mock_db.execute.return_value.fetchone.return_value = {
            "value": generate_password_hash("bar")
        }
        mock_get_db.return_value = mock_db
        response = await self.client.post(
            "/authorize/login",
            form={"password": "foo"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        html = await response.get_data(as_text=True)
        self.assertIn("Invalid password.", html)
        async with self.client.session_transaction() as sess:
            self.assertNotIn("unlocked", sess)

    @patch("openhti.authorize.get_db")
    async def test_validate_valid_password(self, mock_get_db):
        """Test that POST /authorize/login with a valid password sets session['unlocked']."""

        mock_db = MagicMock()
        mock_db.execute.return_value.fetchone.return_value = {
            "value": generate_password_hash("foo")
        }
        mock_get_db.return_value = mock_db
        response = await self.client.post(
            "/authorize/login",
            form={"password": "foo"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        async with self.client.session_transaction() as sess:
            self.assertTrue(sess.get("unlocked"))

    async def test_logout(self):
        """Test that GET /authorize/logout clears the session and redirects to home."""

        async with self.client.session_transaction() as sess:
            sess["unlocked"] = True
        response = await self.client.get(
            "/authorize/logout",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        async with self.client.session_transaction() as sess:
            self.assertNotIn("unlocked", sess)


if __name__ == "__main__":
    main()
