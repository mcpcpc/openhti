from unittest import main
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch
from json import dumps
from urllib.error import HTTPError

from openhti.models.base import Procedure
from openhti.models.archive import ArchiveClient  # Replace with actual module name


class TestArchiveClient(TestCase):
    """Unit tests for the ArchiveClient class."""

    def setUp(self) -> None:
        """Set up common test variables."""

        self.url = "https://example.com/api"
        self.token = "test_token"
        self.client = ArchiveClient(self.url, self.token)

    def test_init(self) -> None:
        """Test ArchiveClient initialization."""

        self.assertEqual(self.client.url, self.url)
        self.assertEqual(self.client.token, self.token)

    def test_headers(self) -> None:
        """Test headers method."""

        expected_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        self.assertEqual(self.client.headers(), expected_headers)

    @patch("openhti.models.archive.urlopen")
    @patch("openhti.models.archive.asdict")
    def test_post_success(self, mock_asdict, mock_urlopen) -> None:
        """Test successful POST request."""

        mock_procedure = MagicMock(spec=Procedure)
        mock_asdict.return_value = {"key": "value"}
        mock_urlopen.return_value.__enter__.return_value = b'{"status": "success"}'
        response = self.client.post(mock_procedure)
        mock_asdict.assert_called_once_with(mock_procedure)
        mock_urlopen.assert_called_once()
        breakpoint()
        self.assertEqual(response, '{"status": "success"}')

    @patch("openhti.models.archive.urlopen")
    def test_post_invalid_procedure(self, mock_urlopen) -> None:
        """Test post method with invalid procedure type."""

        with self.assertRaises(TypeError):
            self.client.post("not_a_procedure")
        mock_urlopen.assert_not_called()


if __name__ == "__main__":
    main()
