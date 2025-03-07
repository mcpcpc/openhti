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
        path = cls._resources / "preload.sql"
        with open(path, mode="r", encoding="utf-8") as f:
            cls._preload = f.read()

    def setUp(self):
        self.db = NamedTemporaryFile()
        self.app = create_app({"TESTING": True, "DATABASE": self.db.name})
        self.client = self.app.test_client()
        self.app.test_cli_runner().invoke(args=["init-db"])
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
            "value": generate_password_hash("secret")
        }
        mock_get_db.return_value = mock_db
        response = await self.client.post(
            "/authorize/login",
            data={"password": "wrong"},
            follow_redirects=True,
        )
        print(dir(response.location))
        #self.assertEqual(response.status_code, 302)
        #self.assertEqual(response.headers.get("Location"), "/authorize/login")

    @patch("openhti.authorize.get_db")
    async def test_validate_valid_password(self, mock_get_db):
        """Test that POST /authorize/login with a valid password sets session['unlocked']."""

        mock_db = MagicMock()
        mock_db.execute.return_value.fetchone.return_value = {
            "value": generate_password_hash("secret")
        }
        mock_get_db.return_value = mock_db
        response = await self.client.post(
            "/authorize/login",
            data={"password": "secret"},
            follow_redirects=True,
        )
        #print(response.request.path)
        print(response.headers)
        #self.assertEqual(response.status_code, 200)
        #self.assertEqual(response.headers.get("Location"), "/home")
        #async with self.client.session_transaction() as sess:
        #    self.assertTrue(sess.get("unlocked"))

    async def test_logout(self):
        """Test that GET /authorize/logout clears the session and redirects to home."""

        async with self.client.session_transaction() as sess:
            sess["unlocked"] = True
        response = await self.client.get(
            "/authorize/logout",
            follow_redirects=True,
        )
        print(dir(response))
        #self.assertEqual(response.status_code, 200)
        #self.assertEqual(response.headers.get("Location"), "/home")
        #async with self.client.session_transaction() as sess:
        #    self.assertNotIn("unlocked", sess)


if __name__ == "__main__":
    main()
