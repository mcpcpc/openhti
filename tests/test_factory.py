#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import IsolatedAsyncioTestCase
from unittest import main

from openhti import create_app


class FactoryTestCase(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.db = "file::memory:?cache=shared"
        self.app = create_app({"TESTING": True, "DATABASE": self.db})
        self.runner = self.app.test_cli_runner()
        self.ctx = self.app.app_context()

    def test_db_close(self) -> None:
        result = self.ctx.g.get("db")
        self.assertIsNone(result, result)

    def test_db_init_command(self) -> None:
        response = self.runner.invoke(args=["init-db"])
        self.assertIsInstance(response.output, str)

    def test_token_command(self) -> None:
        response = self.runner.invoke(args=["token"])
        self.assertIsInstance(response.output, str)


if __name__ == "__main__":
    main()
