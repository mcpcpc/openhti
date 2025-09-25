"""
SPDX-FileCopyrightText: 2025 Gossamer Technologies
SPDX-License-Identifier: BSD-3-Clause

Checksum/database validator methods.
"""

from datetime import datetime
from hashlib import sha256
from json import dumps
from json import JSONEncoder

CHECKSUM_VERSION = b"v1"
CHECKSUM_TABLES = ("command", "instrument", "part", "phase", "procedure", "recipe")


class RecordEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return str(obj)
        return super().default(obj)


def get_checksum(db) -> str:
    """
    Compute a logical, content-level checksum that is stable across
    VACUUM/defrag.
    """

    hashed = sha256()
    hashed.update(CHECKSUM_VERSION)
    for table in CHECKSUM_TABLES:
        rows = db.execute(f"SELECT * FROM {table}").fetchall()
        print(rows)
        records = list(map(dict, rows))
        payload = dumps(records, cls=RecordEncoder)
        hashed.update(payload.encode("utf-8"))
    checksum = hashed.hexdigest()
    return checksum
