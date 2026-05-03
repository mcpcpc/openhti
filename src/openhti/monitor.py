"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Real-time instrument monitoring endpoint.
"""

from asyncio import get_running_loop
from asyncio import sleep as async_sleep
from datetime import datetime
from json import dumps
from json import loads

from quart import Blueprint
from quart import render_template
from quart import websocket

from .database import get_db
from .models.tcp import TCP

monitor = Blueprint("monitor", __name__)


@monitor.get("/monitor")
async def read():
    """Monitor mode read callback."""

    commands = get_db().execute(
        "SELECT * FROM command ORDER BY name"
    ).fetchall()
    instruments = get_db().execute(
        "SELECT * FROM instrument ORDER BY name"
    ).fetchall()
    measurements = get_db().execute(
        "SELECT * FROM measurement ORDER BY name"
    ).fetchall()
    return await render_template(
        "monitor.html",
        commands=commands,
        instruments=instruments,
        measurements=measurements,
    )


@monitor.websocket("/monitor/ws")
async def ws():
    """Monitor websocket — streams samples from an instrument at a set interval."""

    message = await websocket.receive()
    form = loads(message)

    command_id = form["command_id"]
    instrument_id = form["instrument_id"]
    measurement_id = form.get("measurement_id") or None
    interval_ms = max(10, int(form.get("interval_ms", 1000)))

    cmd = dict(
        get_db()
        .execute("SELECT * FROM command WHERE id = ?", (command_id,))
        .fetchone()
    )
    instr = dict(
        get_db()
        .execute("SELECT * FROM instrument WHERE id = ?", (instrument_id,))
        .fetchone()
    )
    meas = None
    if measurement_id:
        row = (
            get_db()
            .execute("SELECT * FROM measurement WHERE id = ?", (measurement_id,))
            .fetchone()
        )
        if row:
            meas = dict(row)

    hostname = instr["hostname"]
    port = instr["port"]
    scpi = cmd["scpi"].encode() + b"\n"
    loop = get_running_loop()

    while True:
        try:
            def _query():
                with TCP(hostname, port) as tcp:
                    return tcp.query(scpi)

            response = await loop.run_in_executor(None, _query)
            value = float(response.decode().strip())
            payload = {
                "value": value,
                "timestamp": datetime.now().timestamp() * 1000,
            }
            if meas:
                payload["lower_limit"] = meas["lower_limit"]
                payload["upper_limit"] = meas["upper_limit"]
                payload["units"] = meas["units"] or ""
                payload["name"] = meas["name"]
                payload["precision"] = meas["precision"]
        except Exception as exc:
            payload = {
                "error": str(exc),
                "timestamp": datetime.now().timestamp() * 1000,
            }

        await websocket.send(dumps(payload))
        await async_sleep(interval_ms / 1000)
