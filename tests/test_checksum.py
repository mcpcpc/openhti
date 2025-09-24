from importlib.resources import read_text
from sqlite3 import connect
from unittest import main
from unittest import TestCase
from unittest.mock import MagicMock


class TestChecksum(TestCase):
    def setUp(self):
        self.db = ":memory:"
        schema = read_text("openhti", "schema.sql")
        self.conn = connect(self.db)
        self.conn.executescript(schema)

    def tearDown(self):
        self.conn.close()

    def test_get_checksum_initialize(self):
        pass 

    def test_get_checksum_change(self):
        pass

    def test_get_checksum_no_change(self):
        pass


if __name__ == "__main__":
    main()
