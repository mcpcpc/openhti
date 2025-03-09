from unittest import main
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch
from socket import SHUT_RDWR

from openhti.models.tcp import TCP


class TestTCP(TestCase):
    """Unit tests for the TCP class."""

    @patch("socket.socket")
    def test_tcp_init(self, mock_socket_class):
        """Test TCP constructor."""

        tcp = TCP("127.0.0.1", 1234)
        self.assertEqual(tcp.hostname, "127.0.0.1")
        self.assertEqual(tcp.port, 1234)
        self.assertIsNone(tcp.sock)

    @patch("socket.socket")
    def test_tcp_context_manager(self, mock_socket):
        """Test TCP context manager (__enter__ and __exit__)."""
    
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        with TCP("127.0.0.1", 1234) as tcp:
            self.assertEqual(tcp.sock, mock_socket_instance)
            mock_socket_instance.settimeout.assert_called_once_with(5)
            mock_socket_instance.connect.assert_called_once_with(("127.0.0.1", 1234))
        mock_socket.shutdown.assert_called_once_with(SHUT_RDWR)
        mock_socket.close.assert_called_once()

    @patch("socket.socket")
    def test_tcp_send(self, mock_socket_class):
        """Test send method."""

        mock_socket = mock_socket_class.return_value
        with TCP("127.0.0.1", 1234) as tcp:
            tcp.send(b"TEST")
            mock_socket.sendall.assert_called_once_with(b"TEST")

    @patch("socket.socket")
    def test_tcp_query(self, mock_socket_class):
        """Test query method with mocked recv response."""

        mock_socket = mock_socket_class.return_value
        mock_socket.recv = MagicMock(
            side_effect=[b"RESPON", b"SE\n"]  # Simulates chunked response
        )
        with TCP("127.0.0.1", 1234) as tcp:
            response = tcp.query(b"QUERY")
            self.assertEqual(response, b"RESPONSE\n")
        mock_socket.sendall.assert_called_once_with(b"QUERY")
        self.assertEqual(mock_socket.recv.call_count, 2)


if __name__ == "__main__":
    main()
