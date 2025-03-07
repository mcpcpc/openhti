#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import IsolatedAsyncioTestCase
from unittest import main
from unittest.mock import patch
from unittest.mock import MagicMock
from unittest.mock import mock_open
from sqlite3 import Connection
from quart import Quart
from pathlib import Path

from openhti.database import get_db
from openhti.database import close_db
from openhti.database import init_db_command
from openhti.database import init_database


class TestDatabase(IsolatedAsyncioTestCase):
    def setUp(self):
        self.app = Quart(__name__)
        self.app.config["DATABASE"] = ":memory:"
        self.app.root_path = "/test/path"

    async def test_get_db(self):
        """Test that `get_db` returns a SQLite connection and reuses it."""

        async with self.app.app_context():
            db1 = get_db()
            self.assertIsInstance(db1, Connection)
            db2 = get_db()
            self.assertIs(db1, db2)

    @patch("openhti.database.connect")
    async def test_close_db(self, mock_connect):
        """Test that `close_db` properly closes the connection."""

        mock_db = MagicMock()
        mock_db.close.return_value = None
        mock_connect.return_value = MagicMock()
        async with self.app.app_context():
            db = get_db()
            await close_db()
        self.assertNotIn("db", self.app.app_context().g)
        mock_db.close.assert_called_once()

    @patch("builtins.open", new_callable=mock_open, read_data="CREATE TABLE test (id INTEGER);")
    @patch("openhti.database.echo")
    def test_init_db_command(self, mock_echo, mock_file):
        """Test that `init_db_command` reads schema and initializes the DB."""
        
        mock_conn = MagicMock()
        with patch("openhti.database.get_db") as mock_get_db:
            mock_get_db.return_value = mock_conn
            runner = self.app.test_cli_runner()
            result = runner.invoke(init_db_command)
            mock_file.assert_called_once_with(Path(self.app.root_path) / "schema.sql")
            mock_conn.executescript.assert_called_once_with("CREATE TABLE test (id INTEGER);")
            mock_echo.assert_called_once_with("Database initialized.")
            self.assertEqual(result.exit_code, 0)

    def test_init_database(self):
        """Test that `init_database` registers teardown and CLI commands."""
        
        mock_app = MagicMock()
        init_database(mock_app)
        mock_app.teardown_appcontext.assert_called_once_with(close_db)
        mock_app.cli.add_command.assert_called_once_with(init_db_command)


if __name__ == "__main__":
    main()
