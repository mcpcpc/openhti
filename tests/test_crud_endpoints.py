"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

CRUD endpoint tests for command, instrument, measurement, part, phase, procedure, recipe, and setting modules.
"""

from tempfile import NamedTemporaryFile
from unittest import IsolatedAsyncioTestCase
from unittest import main

from openhti import create_app


class CRUDTestBase(IsolatedAsyncioTestCase):
    """Base test class for CRUD operations."""

    def setUp(self):
        """Set up test app and database."""

        self.db = NamedTemporaryFile()
        self.app = create_app({"TESTING": True, "DATABASE": self.db.name})
        self.app.test_cli_runner().invoke(args=["init-db"])
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up database."""

        self.db.close()

    async def login(self):
        """Helper to set session as logged in."""

        async with self.client.session_transaction() as sess:
            sess["unlocked"] = True


class CommandCRUDTests(CRUDTestBase):
    """Test command blueprint CRUD operations."""

    async def test_command_read_empty(self):
        """Test reading commands when none exist."""

        await self.login()
        response = await self.client.get("/command")
        self.assertEqual(response.status_code, 200)
        html = await response.get_data(as_text=True)
        self.assertIn("command", html.lower())

    async def test_command_create_success(self):
        """Test creating a command successfully."""

        await self.login()
        response = await self.client.post(
            "/command",
            form={"name": "TestCmd", "scpi": "*IDN?", "delay": "0"},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)

    async def test_command_create_missing_parameters(self):
        """Test creating command with missing parameters."""

        await self.login()
        response = await self.client.post(
            "/command",
            form={"name": "TestCmd"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        html = await response.get_data(as_text=True)
        self.assertIn("Missing parameter", html)

    async def test_command_create_and_read(self):
        """Test creating a command and then reading it."""

        await self.login()
        # Create
        await self.client.post(
            "/command",
            form={"name": "Voltage", "scpi": "VOLT?", "delay": "100"},
        )
        # Read
        response = await self.client.get("/command")
        html = await response.get_data(as_text=True)
        self.assertIn("Voltage", html)

    async def test_command_delete_success(self):
        """Test deleting a command."""

        await self.login()
        # Create
        await self.client.post(
            "/command",
            form={"name": "TempCmd", "scpi": "*RST", "delay": "0"},
        )
        # Get all commands to find ID
        response = await self.client.get("/command")
        html = await response.get_data(as_text=True)
        self.assertIn("TempCmd", html)
        # Delete (would need ID from HTML, simulating with ID 1)
        response = await self.client.post(
            "/command/delete",
            form={"command_id": ["1"]},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)

    async def test_command_update_success(self):
        """Test updating a command."""

        await self.login()
        # Create
        await self.client.post(
            "/command",
            form={"name": "Original", "scpi": "VOLT?", "delay": "0"},
        )
        # Update
        response = await self.client.post(
            "/command/update",
            form={"id": "1", "name": "Updated", "scpi": "CURR?", "delay": "50"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        html = await response.get_data(as_text=True)
        self.assertIn("Updated", html)


class InstrumentCRUDTests(CRUDTestBase):
    """Test instrument blueprint CRUD operations."""

    async def test_instrument_read_empty(self):
        """Test reading instruments when none exist."""

        await self.login()
        response = await self.client.get("/instrument")
        self.assertEqual(response.status_code, 200)
        html = await response.get_data(as_text=True)
        self.assertIn("instrument", html.lower())

    async def test_instrument_create_success(self):
        """Test creating an instrument successfully."""

        await self.login()
        response = await self.client.post(
            "/instrument",
            form={"name": "Multimeter", "hostname": "192.168.1.100", "port": "5025"},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)

    async def test_instrument_create_missing_parameters(self):
        """Test creating instrument with missing parameters."""

        await self.login()
        response = await self.client.post(
            "/instrument",
            form={"name": "TestInstr"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        html = await response.get_data(as_text=True)
        self.assertIn("Missing parameter", html)

    async def test_instrument_create_and_read(self):
        """Test creating an instrument and reading it."""

        await self.login()
        # Create
        await self.client.post(
            "/instrument",
            form={"name": "PowerSupply", "hostname": "10.0.0.1", "port": "5025"},
        )
        # Read
        response = await self.client.get("/instrument")
        html = await response.get_data(as_text=True)
        self.assertIn("PowerSupply", html)

    async def test_instrument_delete_success(self):
        """Test deleting an instrument."""

        await self.login()
        # Create
        await self.client.post(
            "/instrument",
            form={"name": "TempInstr", "hostname": "localhost", "port": "5025"},
        )
        # Delete
        response = await self.client.post(
            "/instrument/delete",
            form={"instrument_id": ["1"]},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)

    async def test_instrument_update_success(self):
        """Test updating an instrument."""

        await self.login()
        # Create
        await self.client.post(
            "/instrument",
            form={"name": "OriginalName", "hostname": "192.168.1.1", "port": "5025"},
        )
        # Update
        response = await self.client.post(
            "/instrument/update",
            form={
                "id": "1",
                "name": "UpdatedName",
                "hostname": "192.168.1.2",
                "port": "5026",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        html = await response.get_data(as_text=True)
        self.assertIn("UpdatedName", html)


class MeasurementCRUDTests(CRUDTestBase):
    """Test measurement blueprint CRUD operations."""

    async def test_measurement_read_empty(self):
        """Test reading measurements when none exist."""

        await self.login()
        response = await self.client.get("/measurement")
        self.assertEqual(response.status_code, 200)
        html = await response.get_data(as_text=True)
        self.assertIn("measurement", html.lower())

    async def test_measurement_create_success(self):
        """Test creating a measurement successfully."""

        await self.login()
        response = await self.client.post(
            "/measurement",
            form={
                "name": "Voltage",
                "precision": "2",
                "units": "V",
                "lower_limit": "4.5",
                "upper_limit": "5.5",
            },
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)

    async def test_measurement_create_missing_parameters(self):
        """Test creating measurement with missing parameters."""

        await self.login()
        response = await self.client.post(
            "/measurement",
            form={"name": "Voltage"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        html = await response.get_data(as_text=True)
        self.assertIn("Missing parameter", html)

    async def test_measurement_create_and_read(self):
        """Test creating measurement and reading it."""

        await self.login()
        # Create
        await self.client.post(
            "/measurement",
            form={
                "name": "Current",
                "precision": "3",
                "units": "A",
                "lower_limit": "0.1",
                "upper_limit": "1.0",
            },
        )
        # Read
        response = await self.client.get("/measurement")
        html = await response.get_data(as_text=True)
        self.assertIn("Current", html)

    async def test_measurement_delete_success(self):
        """Test deleting a measurement."""

        await self.login()
        # Create
        await self.client.post(
            "/measurement",
            form={
                "name": "Temp",
                "precision": "1",
                "units": "C",
                "lower_limit": "-10",
                "upper_limit": "50",
            },
        )
        # Delete
        response = await self.client.post(
            "/measurement/delete",
            form={"measurement_id": ["1"]},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)

    async def test_measurement_update_success(self):
        """Test updating a measurement."""

        await self.login()
        # Create
        await self.client.post(
            "/measurement",
            form={
                "name": "Original",
                "precision": "2",
                "units": "V",
                "lower_limit": "5.0",
                "upper_limit": "5.5",
            },
        )
        # Update
        response = await self.client.post(
            "/measurement/update",
            form={
                "id": "1",
                "name": "Updated",
                "precision": "3",
                "units": "mV",
                "lower_limit": "5000",
                "upper_limit": "5500",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        html = await response.get_data(as_text=True)
        self.assertIn("Updated", html)


class PartCRUDTests(CRUDTestBase):
    """Test part blueprint CRUD operations."""

    async def test_part_read_empty(self):
        """Test reading parts when none exist."""

        await self.login()
        response = await self.client.get("/part")
        self.assertEqual(response.status_code, 200)
        html = await response.get_data(as_text=True)
        self.assertIn("part", html.lower())

    async def test_part_create_success(self):
        """Test creating a part successfully."""

        await self.login()
        response = await self.client.post(
            "/part",
            form={
                "name": "Widget A",
                "global_trade_item_number": "5012345678901",
                "number": "001",
                "revision": "1.0",
            },
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)

    async def test_part_create_and_read(self):
        """Test creating part and reading it."""

        await self.login()
        # Create
        await self.client.post(
            "/part",
            form={
                "name": "Widget B",
                "global_trade_item_number": "5012345678902",
                "number": "002",
                "revision": "2.0",
            },
        )
        # Read
        response = await self.client.get("/part")
        html = await response.get_data(as_text=True)
        self.assertIn("Widget B", html)

    async def test_part_delete_success(self):
        """Test deleting a part."""

        await self.login()
        # Create
        await self.client.post(
            "/part",
            form={
                "name": "TempPart",
                "global_trade_item_number": "5012345678903",
                "number": "003",
                "revision": "1.0",
            },
        )
        # Delete
        response = await self.client.post(
            "/part/delete",
            form={"part_id": ["1"]},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)


class PhaseCRUDTests(CRUDTestBase):
    """Test phase blueprint CRUD operations."""

    async def test_phase_read_empty(self):
        """Test reading phases when none exist."""

        await self.login()
        response = await self.client.get("/phase")
        self.assertEqual(response.status_code, 200)
        html = await response.get_data(as_text=True)
        self.assertIn("phase", html.lower())

    async def test_phase_create_success(self):
        """Test creating a phase successfully."""

        await self.login()
        response = await self.client.post(
            "/phase",
            form={"name": "Initialization"},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)

    async def test_phase_create_and_read(self):
        """Test creating phase and reading it."""

        await self.login()
        # Create
        await self.client.post(
            "/phase",
            form={"name": "Testing"},
        )
        # Read
        response = await self.client.get("/phase")
        html = await response.get_data(as_text=True)
        self.assertIn("Testing", html)

    async def test_phase_delete_success(self):
        """Test deleting a phase."""

        await self.login()
        # Create
        await self.client.post(
            "/phase",
            form={"name": "TempPhase"},
        )
        # Delete
        response = await self.client.post(
            "/phase/delete",
            form={"phase_id": ["1"]},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)


class ProcedureCRUDTests(CRUDTestBase):
    """Test procedure blueprint CRUD operations."""

    async def test_procedure_read_empty(self):
        """Test reading procedures when none exist."""

        await self.login()
        response = await self.client.get("/procedure")
        self.assertEqual(response.status_code, 200)
        html = await response.get_data(as_text=True)
        self.assertIn("procedure", html.lower())

    async def test_procedure_create_success(self):
        """Test creating a procedure successfully."""

        await self.login()
        response = await self.client.post(
            "/procedure",
            form={"name": "Functional Test", "pid": "PROC-001"},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)

    async def test_procedure_create_and_read(self):
        """Test creating procedure and reading it."""

        await self.login()
        # Create
        await self.client.post(
            "/procedure",
            form={"name": "Stress Test", "pid": "PROC-002"},
        )
        # Read
        response = await self.client.get("/procedure")
        html = await response.get_data(as_text=True)
        self.assertIn("Stress Test", html)

    async def test_procedure_delete_success(self):
        """Test deleting a procedure."""

        await self.login()
        # Create
        await self.client.post(
            "/procedure",
            form={"name": "TempProc", "pid": "PROC-TMP"},
        )
        # Delete
        response = await self.client.post(
            "/procedure/delete",
            form={"procedure_id": ["1"]},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)


class RecipeCRUDTests(CRUDTestBase):
    """Test recipe blueprint CRUD operations."""

    async def test_recipe_read_empty(self):
        """Test reading recipes when none exist."""

        await self.login()
        response = await self.client.get("/recipe")
        self.assertEqual(response.status_code, 200)
        html = await response.get_data(as_text=True)
        self.assertIn("recipe", html.lower())


class SettingCRUDTests(CRUDTestBase):
    """Test setting blueprint CRUD operations."""

    async def test_setting_read(self):
        """Test reading settings."""

        await self.login()
        response = await self.client.get("/setting")
        self.assertEqual(response.status_code, 200)
        html = await response.get_data(as_text=True)
        self.assertIn("setting", html.lower())

    async def test_setting_update_basic(self):
        """Test updating settings."""

        await self.login()
        response = await self.client.post(
            "/setting",
            form={
                "password": "newpassword123",
                "pattern": "^SN[0-9]{6}$",
                "archive_url": "https://example.com/api",
                "archive_access_token": "token123",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        html = await response.get_data(as_text=True)
        self.assertIn("Settings updated", html)


class AuthenticationCRUDTests(CRUDTestBase):
    """Test authentication requirement for CRUD operations."""

    async def test_command_read_without_auth(self):
        """Test reading commands without login redirects to login."""

        response = await self.client.get("/command", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        html = await response.get_data(as_text=True)
        self.assertIn("login", html.lower())

    async def test_instrument_create_without_auth(self):
        """Test creating instrument without login redirects to login."""

        response = await self.client.post(
            "/instrument",
            form={"name": "Test", "hostname": "localhost", "port": "5025"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        html = await response.get_data(as_text=True)
        self.assertIn("login", html.lower())

    async def test_measurement_delete_without_auth(self):
        """Test deleting measurement without login redirects to login."""

        response = await self.client.post(
            "/measurement/delete",
            form={"measurement_id": ["1"]},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        html = await response.get_data(as_text=True)
        self.assertIn("login", html.lower())


if __name__ == "__main__":
    main()
