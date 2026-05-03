"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Lightweight hardware test framework application.
"""

from os import makedirs
from os.path import join
from os.path import getmtime

from quart import Quart
from quart import redirect
from quart import url_for

from .api.v1 import api
from .authorize import authorize
from .automatic import automatic
from .database import init_database
from .command import command
from .instrument import instrument
from .manual import manual
from .measurement import measurement
from .monitor import monitor
from .part import part
from .phase import phase
from .procedure import procedure
from .recipe import recipe
from .setting import setting
from .token import init_token

__version__ = "1.0.0"


def init_globals(app: Quart) -> Quart:
    app.jinja_env.globals["app_version"] = __version__

    def static_mtime(filename: str) -> int:
        path = join(app.static_folder, filename)
        try:
            return int(getmtime(path))
        except OSError:
            return 0

    app.jinja_env.globals["static_mtime"] = static_mtime
    return app


def create_app(test_config: dict = None) -> Quart:
    """Application factory."""

    app = Quart(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # Must be >= 32 bytes for HS256 to avoid insecure key warnings.
        SECRET_KEY="openhti-dev-secret-key-change-me-32bytes-min",
        DATABASE=join(app.instance_path, "openhti.db"),
    )
    if test_config is None:
        app.config.from_pyfile(
            "config.py",
            silent=True,
        )
    else:
        app.config.update(test_config)
    try:
        makedirs(app.instance_path)
    except OSError:
        pass

    init_globals(app)
    init_database(app)
    init_token(app)
    app.register_blueprint(api)
    app.register_blueprint(authorize)
    app.register_blueprint(automatic)
    app.register_blueprint(command)
    app.register_blueprint(instrument)
    app.register_blueprint(manual)
    app.register_blueprint(measurement)
    app.register_blueprint(monitor)
    app.register_blueprint(part)
    app.register_blueprint(phase)
    app.register_blueprint(procedure)
    app.register_blueprint(recipe)
    app.register_blueprint(setting)

    @app.get("/")
    async def home():
        return redirect(url_for("automatic.read"))

    return app
