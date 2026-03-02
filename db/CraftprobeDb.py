from typing import Tuple

import aiosqlite
from datetime import datetime, timedelta
import math

class CraftprobeDb:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Python workaround to make a singleton."""
        if cls._instance is None:
            cls._instance = super(CraftprobeDb, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config, db_name="db.sqlite3") -> None:
        self.config = config
        self.db_name = db_name

        # check db exists
        try:
            with open(db_name, 'r') as f:
                pass
        except FileNotFoundError:
            raise Exception(f"Craftprobe database not found.")

    async def is_player_seen(self, username) -> bool:
        username = username.lower()
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT COUNT(*) FROM playername_uuid where lower(player_name) = ?', (username,))
            row = await cursor.fetchall()
            return row[0][0] > 0
        
    async def is_server_seen(self, server_ip) -> bool:
        server_ip = server_ip.split(":")[0]

        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT COUNT(*) FROM servers where server_ip = ?', (server_ip,))
            row = await cursor.fetchall()
            return row[0][0] > 0
