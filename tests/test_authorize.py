#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from sqlite3 import connect
from tempfile import NamedTemporaryFile
from unittest import IsolatedAsyncioTestCase
from unittest import main
from unittest.mock import MagicMock
from unittest.mock import patch

from werkzeug.security import generate_password_hash

from openhti import create_app


class AuthorizeTestCase(IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls._resources = Path(__file__).parent
        path = cls._resources / "data.sql"
        with open(path, mode="r", encoding="utf-8") as f:
            cls._preload = f.read()

    def setUp(self):
        self.db = NamedTemporaryFile()
        self.app = create_app({"TESTING": True, "DATABASE": self.db.name})
        self.app.test_cli_runner().invoke(args=["init-db"])
        self.client = self.app.test_client()
        db = connect(self.db.name)
        db.executescript(self._preload)
        resp = self.app.test_cli_runner().invoke(args=["token"])
        self.token = resp.output.rstrip()

    def tearDown(self):
        self.db.close()

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
            "value": generate_password_hash("foo")
        }
        mock_get_db.return_value = mock_db
        response = await self.client.post(
            "/authorize/login",
            data={"password": "bar"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        html = await response.get_data(as_text=True)
        self.assertIn("Invalid password.", html)

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
            data={"password": "foo"},
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
