#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from sqlite3 import connect
from tempfile import NamedTemporaryFile
from unittest import IsolatedAsyncioTestCase
from unittest import main

from openhti import create_app


class CommandTestCase(IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._resources = Path(__file__).parent
        path = cls._resources / "preload.sql"
        with open(path, mode="r", encoding="utf-8") as f:
            cls._preload = f.read()

    def setUp(self) -> None:
        self.db = NamedTemporaryFile()
        self.app = create_app({"TESTING": True, "DATABASE": self.db.name})
        self.client = self.app.test_client()
        self.app.test_cli_runner().invoke(args=["init-db"])
        db = connect(self.db.name)
        db.executescript(self._preload)
        resp = self.app.test_cli_runner().invoke(args=["token"])
        self.token = resp.output.rstrip()

    def tearDown(self) -> None:
        self.db.close()

    async def test_command_create(self) -> None:
        form = {"name": "name1", "scpi": "scpi1", "delay": 0}
        headers = {"Authorization": f"Bearer {self.token}"}
        response = await self.client.post(
            "/command",
            headers=headers,
            form=form,
            follow_redirects=True,
        )
        print(response.path)
        self.assertEqual(response.headers["Location"], "/command")


if __name__ == "__main__":
    main()
 