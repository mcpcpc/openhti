"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Setting endpoints.
"""

from pathlib import Path

from quart import Blueprint
from quart import current_app
from quart import flash
from quart import redirect
from quart import render_template
from quart import request
from quart import url_for
from werkzeug.security import generate_password_hash

from .authorize import login_required
from .checksum import get_checksum
from .database import get_db

setting = Blueprint("setting", __name__)


@setting.get("/setting")
@login_required
async def read() -> tuple:
    """Read settings callback."""

    settings = get_db().execute("SELECT * FROM setting").fetchall()
    func = lambda s: s["key"] == "checksum"
    checksum = list(filter(func, settings))[0]["value"]
    dirty = checksum != get_checksum()
    return await render_template("setting.html", settings=settings, dirty=dirty)


@setting.post("/setting")
@login_required
async def update() -> tuple:
    """Update settings callback."""

    form = (await request.form).copy().to_dict()
    row = get_db().execute("SELECT * FROM setting WHERE key = 'password'").fetchone()
    if isinstance(form.get("password"), str) and len(form["password"]) > 0:
        form["password"] = generate_password_hash(form["password"])
    else:
        form["password"] = row["value"]
    try:
        db = get_db()
        for key, value in form.items():
            db.execute(
                """
                UPDATE setting SET
                    updated_at = CURRENT_TIMESTAMP,
                    value = ?
                WHERE key = ?
                """,
                (value, key),
            )
        db.commit()
    except db.ProgrammingError:
        await flash("Missing parameter(s).", "warning")
    except db.IntegrityError:
        await flash("Invalid parameter(s).", "warning")
    else:
        await flash("Settings updated.", "success")
    return redirect(url_for(".read"))


@setting.get("/setting/reset")
@login_required
async def reset() -> tuple:
    """Re-initialize the database."""

    db = get_db()
    root_path = Path(current_app.root_path)
    with open(root_path / "schema.sql") as file:
        db.executescript(file.read())
    return redirect(url_for("authorize.logout"))


@setting.get("/setting/clean")
@login_required
async def clean() -> tuple:
    """Reset dirty database to clean."""

    db = get_db()
    db.execute(
        """
        UPDATE setting SET
            updated_at = CURRENT_TIMESTAMP,
            value = ?
        WHERE key = 'checksum'
        """,
        (get_checksum(),),
    )
    db.commit()
    return redirect(url_for("setting.read"))
