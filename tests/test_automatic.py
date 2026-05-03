"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Automatic module tests (recipe execution and archiving).
"""

from unittest import IsolatedAsyncioTestCase
from unittest import main
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch
from tempfile import NamedTemporaryFile

from openhti import create_app
from openhti.automatic import lookup
from openhti.automatic import get_serial_label
from openhti.database import get_db


class AutomaticLookupTests(TestCase):
    """Test lookup function for finding parts by global_trade_item_number."""

    def setUp(self):
        """Set up test app and database."""

        self.db = NamedTemporaryFile()
        self.app = create_app({"TESTING": True, "DATABASE": self.db.name})
        self.app.test_cli_runner().invoke(args=["init-db"])
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        """Clean up."""

        self.ctx.pop()
        self.db.close()

    def test_lookup_existing_part(self):
        """Test lookup finds existing part."""

        db = get_db()
        db.execute(
            "INSERT INTO part(name, global_trade_item_number, number, revision) VALUES (?, ?, ?, ?)",
            ("Widget A", "5012345678901", "001", "1.0"),
        )
        db.commit()

        result = lookup("5012345678901")
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Widget A")
        self.assertEqual(result["global_trade_item_number"], "5012345678901")

    def test_lookup_nonexistent_part(self):
        """Test lookup returns None for non-existent part."""

        result = lookup("9999999999999")
        self.assertIsNone(result)

    def test_lookup_returns_dict(self):
        """Test lookup returns a dictionary."""

        db = get_db()
        db.execute(
            "INSERT INTO part(name, global_trade_item_number, number, revision) VALUES (?, ?, ?, ?)",
            ("Test Part", "5000000000000", "100", "2.0"),
        )
        db.commit()

        result = lookup("5000000000000")
        self.assertIsInstance(result, dict)
        self.assertIn("id", result)
        self.assertIn("name", result)


class AutomaticSerialLabelTests(TestCase):
    """Test serial label extraction with regex patterns."""

    def setUp(self):
        """Set up test app and database with pattern setting."""

        self.db = NamedTemporaryFile()
        self.app = create_app({"TESTING": True, "DATABASE": self.db.name})
        self.app.test_cli_runner().invoke(args=["init-db"])
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        """Clean up."""

        self.ctx.pop()
        self.db.close()

    def test_get_serial_label_matches_pattern(self):
        """Test extracting serial label with matching pattern."""

        db = get_db()
        db.execute(
            "UPDATE setting SET value = ? WHERE key = ?",
            ("^SN[0-9]{6}$", "pattern"),
        )
        db.commit()

        result = get_serial_label("SN123456")
        self.assertIsNotNone(result)
        self.assertEqual(result.group(0), "SN123456")

    def test_get_serial_label_no_match(self):
        """Test extracting serial label when pattern doesn't match."""

        db = get_db()
        db.execute(
            "UPDATE setting SET value = ? WHERE key = ?",
            ("^SN[0-9]{6}$", "pattern"),
        )
        db.commit()

        result = get_serial_label("INVALID")
        self.assertIsNone(result)

    def test_get_serial_label_partial_match(self):
        """Test extracting serial label with partial match."""

        db = get_db()
        db.execute(
            "UPDATE setting SET value = ? WHERE key = ?",
            ("SN[0-9]{3}", "pattern"),
        )
        db.commit()

        result = get_serial_label("SN123456")
        self.assertIsNotNone(result)
        self.assertEqual(result.group(0), "SN123")


class AutomaticArchiveTests(TestCase):
    """Test archive posting functionality."""

    def setUp(self):
        """Set up test app and database."""

        self.db = NamedTemporaryFile()
        self.app = create_app({"TESTING": True, "DATABASE": self.db.name})
        self.app.test_cli_runner().invoke(args=["init-db"])
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        """Clean up."""

        self.ctx.pop()
        self.db.close()

    @patch("openhti.automatic.ArchiveClient")
    def test_archive_with_valid_settings(self, mock_archive_client_class):
        """Test archiving with valid URL and token."""

        from openhti.automatic import archive
        from openhti.models.base import Procedure
        from openhti.models.base import UnitUnderTest

        db = get_db()
        db.execute(
            "UPDATE setting SET value = ? WHERE key = ?",
            ("https://archive.example.com/api", "archive_url"),
        )
        db.execute(
            "UPDATE setting SET value = ? WHERE key = ?",
            ("token123", "archive_access_token"),
        )
        db.commit()

        mock_client = MagicMock()
        mock_archive_client_class.return_value = mock_client

        procedure = Procedure(
            procedure_id="PROC-001",
            procedure_name="Test",
            unit_under_test=UnitUnderTest(serial_number="SN123"),
        )

        archive(procedure)
        mock_archive_client_class.assert_called_once_with(
            "https://archive.example.com/api", "token123"
        )
        mock_client.post.assert_called_once()

    @patch("openhti.automatic.ArchiveClient")
    def test_archive_without_url(self, mock_archive_client_class):
        """Test archiving is skipped when URL is not configured."""

        from openhti.automatic import archive
        from openhti.models.base import Procedure
        from openhti.models.base import UnitUnderTest

        db = get_db()
        db.execute(
            "UPDATE setting SET value = ? WHERE key = ?",
            ("", "archive_url"),
        )
        db.commit()

        procedure = Procedure(
            procedure_id="PROC-001",
            procedure_name="Test",
            unit_under_test=UnitUnderTest(serial_number="SN123"),
        )

        archive(procedure)
        mock_archive_client_class.assert_not_called()

    @patch("openhti.automatic.ArchiveClient")
    def test_archive_without_token(self, mock_archive_client_class):
        """Test archiving is skipped when token is not configured."""

        from openhti.automatic import archive
        from openhti.models.base import Procedure
        from openhti.models.base import UnitUnderTest

        db = get_db()
        db.execute(
            "UPDATE setting SET value = ? WHERE key = ?",
            ("https://archive.example.com/api", "archive_url"),
        )
        db.execute(
            "UPDATE setting SET value = ? WHERE key = ?",
            ("", "archive_access_token"),
        )
        db.commit()

        procedure = Procedure(
            procedure_id="PROC-001",
            procedure_name="Test",
            unit_under_test=UnitUnderTest(serial_number="SN123"),
        )

        archive(procedure)
        mock_archive_client_class.assert_not_called()

    @patch("openhti.automatic.ArchiveClient")
    def test_archive_exception_handling(self, mock_archive_client_class):
        """Test archiving handles exceptions gracefully."""

        from openhti.automatic import archive
        from openhti.models.base import Procedure
        from openhti.models.base import UnitUnderTest

        db = get_db()
        db.execute(
            "UPDATE setting SET value = ? WHERE key = ?",
            ("https://archive.example.com/api", "archive_url"),
        )
        db.execute(
            "UPDATE setting SET value = ? WHERE key = ?",
            ("token123", "archive_access_token"),
        )
        db.commit()

        mock_client = MagicMock()
        mock_client.post.side_effect = Exception("Network error")
        mock_archive_client_class.return_value = mock_client

        procedure = Procedure(
            procedure_id="PROC-001",
            procedure_name="Test",
            unit_under_test=UnitUnderTest(serial_number="SN123"),
        )

        # Should not raise exception
        try:
            archive(procedure)
        except Exception as e:
            self.fail(f"archive() raised {e}")


class AutomaticRecipeSelectQueryTests(TestCase):
    """Test recipe SQL query construction."""

    def setUp(self):
        """Set up test app and database."""

        self.db = NamedTemporaryFile()
        self.app = create_app({"TESTING": True, "DATABASE": self.db.name})
        self.app.test_cli_runner().invoke(args=["init-db"])
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        """Clean up."""

        self.ctx.pop()
        self.db.close()

    def test_recipe_query_joins_all_tables(self):
        """Test recipe query properly joins all required tables."""

        from openhti.automatic import recipe_select_query

        # Query should contain all required JOINs
        self.assertIn("INNER JOIN", recipe_select_query)
        self.assertIn("command", recipe_select_query)
        self.assertIn("instrument", recipe_select_query)
        self.assertIn("measurement", recipe_select_query)
        self.assertIn("phase", recipe_select_query)
        self.assertIn("procedure", recipe_select_query)

    def test_recipe_query_filters_by_part_and_procedure(self):
        """Test recipe query filters by part and procedure IDs."""

        from openhti.automatic import recipe_select_query

        self.assertIn("part.id = ?", recipe_select_query)
        self.assertIn("procedure.id = ?", recipe_select_query)


class AutomaticWebsocketTests(IsolatedAsyncioTestCase):
    """Test automatic websocket endpoint."""

    def setUp(self):
        """Set up test app and database."""

        self.db = NamedTemporaryFile()
        self.app = create_app({"TESTING": True, "DATABASE": self.db.name})
        self.app.test_cli_runner().invoke(args=["init-db"])
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up."""

        self.db.close()

    async def test_automatic_endpoint_exists(self):
        """Test that automatic endpoint exists."""

        response = await self.client.get("/automatic")
        # Should return 200 (page exists)
        self.assertEqual(response.status_code, 200)

    async def test_automatic_page_contains_template(self):
        """Test that automatic page renders properly."""

        response = await self.client.get("/automatic")
        html = await response.get_data(as_text=True)
        # Should contain some content
        self.assertGreater(len(html), 0)


if __name__ == "__main__":
    main()
