from importlib.resources import files
from sqlite3 import connect
from unittest import main
from unittest import TestCase
from unittest.mock import MagicMock


class TestChecksum(TestCase):
    def setUp(self):
        self.db = ":memory:"
        self.files = files("openhti")
        self.path = files.joinpath("schema.sql")
        self.conn = connect(self.db)
        with open(self.path, "r") as file:
            schema = file.read()
        self.conn.executescript(schema)

    def tearDown(self):
        self.conn.close()

    def test_get_checksum_initialize(self):
        pass 

    def test_get_checksum_change(self):
        pass

    def test_get_checksum_no_change(self):
        pass


if __init__ == "__main__":
    main()
