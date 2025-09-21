"""
SPDX-FileCopyrightText: 2024 Gossamer Technologies
SPDX-License-Identifier: BSD-3-Clause

Database initializer.
"""

from datetime import datetime
from hashlib import sha256
from pathlib import Path
from sqlite3 import connect
from sqlite3 import PARSE_DECLTYPES
from sqlite3 import register_converter
from sqlite3 import Row

from click import command
from click import echo
from quart import current_app
from quart import g
from quart.cli import with_appcontext

CHECKSUM_TABLE_NAMES = ("command", "instrument", "part", "phase", "procedure", "recipe")


def convert_datetime(value: bytes):
    """
    Convert ISO 8601 datetime to datetime.datetime object.
    """

    return datetime.fromisoformat(value.decode())


def get_db():
    """
    Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """

    if not hasattr(g, "db"):
        register_converter("datetime", convert_datetime)
        g.db = connect(
            current_app.config["DATABASE"],
            detect_types=PARSE_DECLTYPES,
        )
        g.db.row_factory = Row
    return g.db


async def close_db(exception=None):
    """
    If this request connected to the database, close the connection.
    """

    db = g.pop("db", None)
    if db is not None:
        db.close()


@command("init-db")
@with_appcontext
def init_db_command() -> None:
    """
    Clear existing data and create new tables.
    """

    db = get_db()
    root_path = Path(current_app.root_path)
    with open(root_path / "schema.sql") as file:
        db.executescript(file.read())
    echo("Database initialized.")


def init_database(app) -> None:
    """
    Register database functions with the Quart app. This is called by
    the application factory.
    """

    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def get_checksum():
    db = get_db()
    checksum = sha256()
    for table in CHECKSUM_TABLE_NAMES:
        rows = db.execute(f"SELECT * FROM {table}").fetchall()
        if len(rows) == 0:
            continue  # no data
        row_c = max(rows, key=lambda r: r["created_at"])
        rows_f = list(filter(lambda r: r["updated_at"], rows))
        if len(rows_f) == 0:
            row_u = {"updated_at": None}
        else:
            row_u = max(rows_f, key=lambda r: r["updated_at"])
        if row_u["updated_at"] is None:
            ts = str(row_c["created_at"])
        else:
            if row_c["created_at"] > row_u["updated_at"]:
                ts = str(row_c["created_at"])
            else:
                ts = str(row_u["updated_at"])
        checksum.update(ts.encode("utf-8"))
    return checksum.hexdigest()
