#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from datetime import timedelta
from datetime import timezone
from unittest import IsolatedAsyncioTestCase
from unittest import main
from unittest.mock import patch
from unittest.mock import MagicMock

from quart import Quart
from jwt import encode

from openhti.token import token_required


class TestToken(IsolatedAsyncioTestCase):
    def setUp(self):
        self.app = Quart(__name__)
        self.app.config["DATABASE"] = ":memory:"
        self.app.config["SECRET_KEY"] = "secret"

    @patch("openhti.token.request")
    async def test_token_required_valid(self, mock_request):
        """Test token_required decorator with a valid token."""

        token = encode(
            {"confirm": "42", "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=300)},
            key=self.app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        mock_request.headers.return_value = {
            "Authorization": f"Bearer {token}",
        }
        mock_view = MagicMock()
        mock_view.return_value = "Success"
        with self.app.app_context():
            wrapped_view = token_required(self.mock_view)
            result, status = await wrapped_view()
        breakpoint() 
        #self.assertEqual(result, "Success")
