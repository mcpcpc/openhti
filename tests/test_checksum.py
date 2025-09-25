from importlib.resources import files
from sqlite3 import connect
from sqlite3 import Row
from unittest import main
from unittest import TestCase
from unittest.mock import MagicMock
from openhti.checksum import get_checksum


class TestChecksum(TestCase):
    def setUp(self):
        self.db = ":memory:"
        self.expected = "797388c088731761d77edfd27335aff46ec07bf5ff23c3dd0d4fda8b4bbb43dc"
        #self.schema = read_text("openhti", "schema.sql")
        path = files("openhti").joinpath("schema.sql")
        self.schema = path.read_text(encoding="utf-8")
        self.conn = connect(self.db)
        self.conn.row_factory = Row
        self.conn.executescript(self.schema)

    def tearDown(self):
        self.conn.close()

    def test_get_checksum_initialize(self):
        result = get_checksum(self.conn)
        self.assertEqual(result, self.expected) 

    def test_get_checksum_change(self):
        self.conn.execute(
            """
            INSERT INTO phase(name) VALUES
                ("test value");
            """
        )
        self.conn.commit()
        result = get_checksum(self.conn)
        self.assertNotEqual(result, self.expected)

    def test_get_checksum_no_change(self):
        pass


if __name__ == "__main__":
    main()
