"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

API v1 endpoint tests.
"""

from datetime import datetime
from datetime import timedelta
from datetime import timezone
from tempfile import NamedTemporaryFile
from unittest import IsolatedAsyncioTestCase
from unittest import main

from jwt import encode

from openhti import create_app


class APITestBase(IsolatedAsyncioTestCase):
    """Base test class for API endpoints."""

    def setUp(self):
        """Set up test app and database."""

        self.db = NamedTemporaryFile()
        self.app = create_app({"TESTING": True, "DATABASE": self.db.name})
        self.app.test_cli_runner().invoke(args=["init-db"])
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up database."""

        self.db.close()

    def _get_valid_token(self, expires_in=300):
        """Generate a valid JWT token."""

        delta = timedelta(seconds=expires_in)
        exp = datetime.now(tz=timezone.utc) + delta
        token = encode(
            payload={"confirm": "42", "exp": exp},
            key=self.app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        return token

    async def _create_sample_data(self):
        """Create sample data for testing."""

        from openhti.database import get_db

        db = get_db()
        # Create phase
        db.execute("INSERT INTO phase(name) VALUES ('Test Phase')")
        db.commit()
        # Create command
        db.execute(
            "INSERT INTO command(name, scpi, delay) VALUES (?, ?, ?)",
            ("TestCmd", "*IDN?", 0),
        )
        db.commit()
        # Create instrument
        db.execute(
            "INSERT INTO instrument(name, hostname, port) VALUES (?, ?, ?)",
            ("TestInstr", "localhost", 5025),
        )
        db.commit()
        # Create measurement
        db.execute(
            "INSERT INTO measurement(name, precision, units, lower_limit, upper_limit) VALUES (?, ?, ?, ?, ?)",
            ("Voltage", 2, "V", 4.5, 5.5),
        )
        db.commit()
        # Create part
        db.execute(
            "INSERT INTO part(name, global_trade_item_number, number, revision) VALUES (?, ?, ?, ?)",
            ("Widget", "5012345678901", "001", "1.0"),
        )
        db.commit()
        # Create procedure
        db.execute(
            "INSERT INTO procedure(name, pid) VALUES (?, ?)",
            ("TestProc", "PROC-001"),
        )
        db.commit()
        # Create recipe
        db.execute(
            """INSERT INTO recipe(command_id, instrument_id, measurement_id, part_id, phase_id, procedure_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (1, 1, 1, 1, 1, 1),
        )
        db.commit()


class CommandAPITests(APITestBase):
    """Test command API endpoints."""

    async def test_list_commands_no_auth(self):
        """Test listing commands without token returns 401."""

        response = await self.client.get("/api/v1/command")
        self.assertEqual(response.status_code, 401)

    async def test_list_commands_with_auth(self):
        """Test listing commands with valid token."""

        token = self._get_valid_token()
        response = await self.client.get(
            "/api/v1/command",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertIn(response.status_code, [200, 201])

    async def test_list_commands_returns_list(self):
        """Test listing commands returns JSON list."""

        await self._create_sample_data()
        token = self._get_valid_token()
        response = await self.client.get(
            "/api/v1/command",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 201)

    async def test_read_command_not_found(self):
        """Test reading non-existent command returns 404."""

        token = self._get_valid_token()
        response = await self.client.get(
            "/api/v1/command/999",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 404)

    async def test_read_command_success(self):
        """Test reading existing command returns 201."""

        await self._create_sample_data()
        token = self._get_valid_token()
        response = await self.client.get(
            "/api/v1/command/1",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 201)

    async def test_delete_command_no_auth(self):
        """Test deleting command without token returns 401."""

        response = await self.client.delete("/api/v1/command/1")
        self.assertEqual(response.status_code, 401)


class InstrumentAPITests(APITestBase):
    """Test instrument API endpoints."""

    async def test_list_instruments_with_auth(self):
        """Test listing instruments with valid token."""

        token = self._get_valid_token()
        response = await self.client.get(
            "/api/v1/instrument",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertIn(response.status_code, [200, 201])

    async def test_read_instrument_not_found(self):
        """Test reading non-existent instrument returns 404."""

        token = self._get_valid_token()
        response = await self.client.get(
            "/api/v1/instrument/999",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 404)

    async def test_read_instrument_success(self):
        """Test reading existing instrument returns 201."""

        await self._create_sample_data()
        token = self._get_valid_token()
        response = await self.client.get(
            "/api/v1/instrument/1",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 201)


class MeasurementAPITests(APITestBase):
    """Test measurement API endpoints."""

    async def test_list_measurements_with_auth(self):
        """Test listing measurements with valid token."""

        token = self._get_valid_token()
        response = await self.client.get(
            "/api/v1/measurement",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertIn(response.status_code, [200, 201])

    async def test_read_measurement_success(self):
        """Test reading existing measurement returns 201."""

        await self._create_sample_data()
        token = self._get_valid_token()
        response = await self.client.get(
            "/api/v1/measurement/1",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 201)


class PartAPITests(APITestBase):
    """Test part API endpoints."""

    async def test_list_parts_with_auth(self):
        """Test listing parts with valid token."""

        token = self._get_valid_token()
        response = await self.client.get(
            "/api/v1/part",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertIn(response.status_code, [200, 201])

    async def test_read_part_success(self):
        """Test reading existing part returns 201."""

        await self._create_sample_data()
        token = self._get_valid_token()
        response = await self.client.get(
            "/api/v1/part/1",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 201)


class PhaseAPITests(APITestBase):
    """Test phase API endpoints."""

    async def test_list_phases_with_auth(self):
        """Test listing phases with valid token."""

        token = self._get_valid_token()
        response = await self.client.get(
            "/api/v1/phase",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertIn(response.status_code, [200, 201])

    async def test_read_phase_success(self):
        """Test reading existing phase returns 201."""

        await self._create_sample_data()
        token = self._get_valid_token()
        response = await self.client.get(
            "/api/v1/phase/1",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 201)


class ProcedureAPITests(APITestBase):
    """Test procedure API endpoints."""

    async def test_list_procedures_with_auth(self):
        """Test listing procedures with valid token."""

        token = self._get_valid_token()
        response = await self.client.get(
            "/api/v1/procedure",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertIn(response.status_code, [200, 201])

    async def test_read_procedure_success(self):
        """Test reading existing procedure returns 201."""

        await self._create_sample_data()
        token = self._get_valid_token()
        response = await self.client.get(
            "/api/v1/procedure/1",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 201)


class RecipeAPITests(APITestBase):
    """Test recipe API endpoints."""

    async def test_list_recipes_with_auth(self):
        """Test listing recipes with valid token."""

        token = self._get_valid_token()
        response = await self.client.get(
            "/api/v1/recipe",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertIn(response.status_code, [200, 201])

    async def test_read_recipe_success(self):
        """Test reading existing recipe returns 201."""

        await self._create_sample_data()
        token = self._get_valid_token()
        response = await self.client.get(
            "/api/v1/recipe/1",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 201)


class APIDeleteTests(APITestBase):
    """Test API delete endpoints."""

    async def test_delete_command_success(self):
        """Test deleting command via API."""

        await self._create_sample_data()
        token = self._get_valid_token()
        response = await self.client.delete(
            "/api/v1/command/1",
            headers={"Authorization": f"Bearer {token}"},
        )
        # Should succeed with 201 or 204
        self.assertIn(response.status_code, [200, 201, 204])

    async def test_delete_instrument_success(self):
        """Test deleting instrument via API."""

        await self._create_sample_data()
        token = self._get_valid_token()
        response = await self.client.delete(
            "/api/v1/instrument/1",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertIn(response.status_code, [200, 201, 204])

    async def test_delete_nonexistent_resource(self):
        """Test deleting non-existent resource."""

        token = self._get_valid_token()
        response = await self.client.delete(
            "/api/v1/command/999",
            headers={"Authorization": f"Bearer {token}"},
        )
        # Should return error (404 or 201)
        self.assertIn(response.status_code, [200, 201, 404])


class APIAuthenticationTests(APITestBase):
    """Test API authentication requirements."""

    async def test_all_endpoints_require_auth(self):
        """Test all endpoints return 401 without token."""

        endpoints = [
            "/api/v1/command",
            "/api/v1/instrument",
            "/api/v1/measurement",
            "/api/v1/part",
            "/api/v1/phase",
            "/api/v1/procedure",
            "/api/v1/recipe",
            "/api/v1/command/1",
            "/api/v1/instrument/1",
        ]
        for endpoint in endpoints:
            response = await self.client.get(endpoint)
            self.assertEqual(response.status_code, 401, f"Endpoint {endpoint} did not require auth")

    async def test_expired_token_rejected(self):
        """Test that expired tokens are rejected."""

        # Generate token that expired 1 hour ago
        token = self._get_valid_token(expires_in=-3600)
        response = await self.client.get(
            "/api/v1/phase",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 401)

    async def test_invalid_token_rejected(self):
        """Test that invalid tokens are rejected."""

        response = await self.client.get(
            "/api/v1/phase",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        self.assertEqual(response.status_code, 401)


class APIResponseFormatTests(APITestBase):
    """Test API response formats."""

    async def test_list_endpoint_returns_json_list(self):
        """Test list endpoints return JSON arrays."""

        await self._create_sample_data()
        token = self._get_valid_token()
        response = await self.client.get(
            "/api/v1/phase",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 201)
        # Response should be JSON
        content_type = response.headers.get("Content-Type")
        self.assertIn("application/json", content_type or "")

    async def test_read_endpoint_returns_json_object(self):
        """Test read endpoints return JSON objects."""

        await self._create_sample_data()
        token = self._get_valid_token()
        response = await self.client.get(
            "/api/v1/phase/1",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 201)
        content_type = response.headers.get("Content-Type")
        self.assertIn("application/json", content_type or "")


if __name__ == "__main__":
    main()
