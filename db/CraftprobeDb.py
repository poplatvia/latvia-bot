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
        
    # preprocessing. Remove all invalid minecraft usernames.
    async def preprocess(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('DELETE FROM playername_uuid WHERE player_name NOT GLOB "[a-zA-Z0-9_]*" or length(player_name) < 3 or length(player_name) > 16')
            await db.commit()

    async def is_player_seen(self, username) -> bool:
        username = username.lower()
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT COUNT(*) FROM playername_uuid where lower(player_name) = ?', (username,))
            row = await cursor.fetchall()
            return row[0][0] > 0
        
    async def when_was_player_seen(self, username) -> list[datetime] | None:
        username = username.lower()
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT player_uuid FROM playername_uuid where lower(player_name) = ?', (username,))
            row = await cursor.fetchall()
            if len(row) == 0:
                return None
            cursor = await db.execute('SELECT last_updated FROM players_seen where player_uuid = ?', (row[0][0],))
            row = await cursor.fetchall()
            if len(row) == 0:
                return None
            # loop through all rows and return a list of timestamps
            timestamps = []
            for row in row:
                timestamps.append(datetime.fromisoformat(row[0]))
            return timestamps
        
    async def is_server_seen(self, server_ip) -> bool:
        server_ip = server_ip.split(":")[0]

        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT COUNT(*) FROM servers where server_ip = ?', (server_ip,))
            row = await cursor.fetchall()
            return row[0][0] > 0
