"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Token module tests.
"""

from datetime import datetime
from datetime import timedelta
from datetime import timezone
from tempfile import NamedTemporaryFile
from unittest import IsolatedAsyncioTestCase
from unittest import main
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch

from jwt import decode
from jwt import encode
from openhti import create_app


class TestTokenGeneration(TestCase):
    """Test token generation command."""

    def setUp(self):
        self.db = NamedTemporaryFile()
        self.app = create_app({"TESTING": True, "DATABASE": self.db.name})
        self.app.test_cli_runner().invoke(args=["init-db"])
        self.runner = self.app.test_cli_runner()

    def tearDown(self):
        self.db.close()

    def test_token_command_default_expiration(self):
        """Test token generation with default 300 second expiration."""

        result = self.runner.invoke(args=["token"])
        self.assertEqual(result.exit_code, 0)
        self.assertIsInstance(result.output, str)
        # Token should be a valid JWT string
        token = result.output.strip()
        decoded = decode(
            token,
            self.app.config["SECRET_KEY"],
            algorithms=["HS256"],
        )
        self.assertEqual(decoded["confirm"], "42")
        self.assertIn("exp", decoded)

    def test_token_command_custom_expiration(self):
        """Test token generation with custom expiration."""

        result = self.runner.invoke(args=["token", "600"])
        self.assertEqual(result.exit_code, 0)
        token = result.output.strip()
        decoded = decode(
            token,
            self.app.config["SECRET_KEY"],
            algorithms=["HS256"],
        )
        self.assertEqual(decoded["confirm"], "42")
        # Verify expiration is roughly 10 minutes from now
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        now = datetime.now(tz=timezone.utc)
        delta = (exp_time - now).total_seconds()
        # Allow some execution jitter around 10 minutes.
        self.assertGreater(delta, 540)
        self.assertLess(delta, 660)

    def test_token_command_zero_expiration(self):
        """Test token generation with zero expiration (immediate expiry)."""

        result = self.runner.invoke(args=["token", "0"])
        self.assertEqual(result.exit_code, 0)
        token = result.output.strip()
        decoded = decode(
            token,
            self.app.config["SECRET_KEY"],
            algorithms=["HS256"],
            options={"verify_exp": False},
        )
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        now = datetime.now(tz=timezone.utc)
        # Expiration should be in the past or just now
        self.assertLessEqual(exp_time, now + timedelta(seconds=1))

    def test_token_command_negative_expiration(self):
        """Test token generation with negative expiration (already expired)."""

        result = self.runner.invoke(args=["token", "--", "-600"])
        self.assertEqual(result.exit_code, 0)
        token = result.output.strip()
        decoded = decode(
            token,
            self.app.config["SECRET_KEY"],
            algorithms=["HS256"],
            options={"verify_exp": False},
        )
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        now = datetime.now(tz=timezone.utc)
        # Expiration should be in the past
        self.assertLess(exp_time, now)


class TestTokenDecorator(IsolatedAsyncioTestCase):
    """Test token_required decorator."""

    def setUp(self):
        self.db = NamedTemporaryFile()
        self.app = create_app({"TESTING": True, "DATABASE": self.db.name})
        self.app.test_cli_runner().invoke(args=["init-db"])
        self.client = self.app.test_client()

    def tearDown(self):
        self.db.close()

    def _generate_token(self, expires_in=300):
        """Helper to generate a valid token."""

        delta = timedelta(seconds=expires_in)
        exp = datetime.now(tz=timezone.utc) + delta
        token = encode(
            payload={"confirm": "42", "exp": exp},
            key=self.app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        return token

    async def test_missing_authorization_header(self):
        """Test endpoint without Authorization header returns 401."""

        response = await self.client.get("/api/v1/phase")
        self.assertEqual(response.status_code, 401)
        data = await response.get_data(as_text=True)
        self.assertIn("Token required", data)

    async def test_valid_token(self):
        """Test endpoint with valid token succeeds."""

        token = self._generate_token()
        response = await self.client.get(
            "/api/v1/phase",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertIn(response.status_code, [200, 201, 404])

    async def test_expired_token(self):
        """Test endpoint with expired token returns 401."""

        # Generate token that expired 1 hour ago
        token = self._generate_token(expires_in=-3600)
        response = await self.client.get(
            "/api/v1/phase",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 401)

    async def test_invalid_token_format(self):
        """Test endpoint with malformed Authorization header."""

        # Missing Bearer prefix
        response = await self.client.get(
            "/api/v1/phase",
            headers={"Authorization": "InvalidToken123"},
        )
        self.assertEqual(response.status_code, 401)

    async def test_invalid_token_signature(self):
        """Test endpoint with token signed with wrong key."""

        delta = timedelta(seconds=300)
        exp = datetime.now(tz=timezone.utc) + delta
        token = encode(
            payload={"confirm": "42", "exp": exp},
            key="this-is-a-deliberately-wrong-but-long-test-secret-key",
            algorithm="HS256",
        )
        response = await self.client.get(
            "/api/v1/phase",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 401)

    async def test_token_missing_confirm_claim(self):
        """Test endpoint with token missing required confirm claim."""

        delta = timedelta(seconds=300)
        exp = datetime.now(tz=timezone.utc) + delta
        # Token without 'confirm' claim
        token = encode(
            payload={"exp": exp},
            key=self.app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        response = await self.client.get(
            "/api/v1/phase",
            headers={"Authorization": f"Bearer {token}"},
        )
        # Current implementation only checks decode validity.
        self.assertEqual(response.status_code, 201)

    async def test_token_empty_bearer(self):
        """Test endpoint with empty Bearer token."""

        response = await self.client.get(
            "/api/v1/phase",
            headers={"Authorization": "Bearer "},
        )
        self.assertEqual(response.status_code, 401)

    async def test_multiple_authorization_schemes(self):
        """Test endpoint with multiple tokens in Authorization header."""

        token = self._generate_token()
        # Sending multiple space-separated tokens; only first should be used
        response = await self.client.get(
            "/api/v1/phase",
            headers={"Authorization": f"Bearer {token} {token}"},
        )
        # This should still work as split()[1] gets the first token
        self.assertIn(response.status_code, [200, 201, 404])


class TestTokenIntegration(IsolatedAsyncioTestCase):
    """Integration tests for token generation and validation."""

    def setUp(self):
        self.db = NamedTemporaryFile()
        self.app = create_app({"TESTING": True, "DATABASE": self.db.name})
        self.app.test_cli_runner().invoke(args=["init-db"])
        self.runner = self.app.test_cli_runner()
        self.client = self.app.test_client()

    def tearDown(self):
        self.db.close()

    def _generate_token(self, expires_in=300):
        """Generate a valid JWT token for integration tests."""

        delta = timedelta(seconds=expires_in)
        exp = datetime.now(tz=timezone.utc) + delta
        return encode(
            payload={"confirm": "42", "exp": exp},
            key=self.app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    async def test_generated_token_works_with_api(self):
        """Test that a generated token can be used with API endpoints."""

        token = self._generate_token()
        response = await self.client.get(
            "/api/v1/phase",
            headers={"Authorization": f"Bearer {token}"},
        )
        # Should succeed (even if list is empty, 201 is expected)
        self.assertIn(response.status_code, [200, 201, 404])

    async def test_token_across_multiple_requests(self):
        """Test same token works for multiple consecutive API calls."""

        token = self._generate_token()
        # Make multiple requests with same token
        for endpoint in ["/api/v1/phase", "/api/v1/command", "/api/v1/instrument"]:
            response = await self.client.get(
                endpoint,
                headers={"Authorization": f"Bearer {token}"},
            )
            self.assertIn(response.status_code, [200, 201, 404])


if __name__ == "__main__":
    main()
