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
            await db.execute('DELETE FROM players_seen WHERE player_uuid NOT IN (SELECT player_uuid FROM playername_uuid)')
            await db.commit()
            await db.execute('DELETE FROM inactive_servers')
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
        
    async def is_server_seen(self, server_ip, port) -> bool:
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT COUNT(*) FROM servers where server_ip = ? AND port = ?', (server_ip, port))
            row = await cursor.fetchall()
            return row[0][0] > 0
        
    async def get_random_server(self, version: str=None) -> str | None:
        async with aiosqlite.connect(self.db_name) as db:
            if version:
                # union the servers table with the players_seen table to get a random server that has been seen with the specified version
                cursor = await db.execute('SELECT server_ip, port FROM servers WHERE server_version = ? AND sorted_tag = "unsorted" AND concat(server_ip, ":", port) IN (SELECT server FROM players_seen) ORDER BY RANDOM() LIMIT 1', (version,))
            else:
                cursor = await db.execute('SELECT server_ip, port FROM servers WHERE sorted_tag = "unsorted" AND concat(server_ip, ":", port) IN (SELECT server FROM players_seen) ORDER BY RANDOM() LIMIT 1')
            row = await cursor.fetchall()
            if len(row) == 0:
                return None

            return f"{row[0][0]}:{row[0][1]}"
    
    async def mark_server_as_whitelisted(self, server_ip) -> bool:
        server = server_ip.split(":")[0]
        port = server_ip.split(":")[1]
        # return false if no such server exists
        if not await self.is_server_seen(server, port):
            return False
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE servers SET sorted_tag = "user_whitelist" WHERE server_ip = ? AND port = ?', (server, port))
            await db.commit()
        return True
    
    async def mark_server_as_hub(self, server_ip) -> bool:
        server = server_ip.split(":")[0]
        port = server_ip.split(":")[1]
        # return false if no such server exists
        if not await self.is_server_seen(server, port):
            return False
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE servers SET sorted_tag = "user_hub" WHERE server_ip = ? AND port = ?', (server, port))
            await db.commit()
        return True
    
    async def mark_server_as_modded(self, server_ip) -> bool:
        server = server_ip.split(":")[0]
        port = server_ip.split(":")[1]
        # return false if no such server exists
        if not await self.is_server_seen(server, port):
            return False
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE servers SET sorted_tag = "user_modded" WHERE server_ip = ? AND port = ?', (server, port))
            await db.commit()
        return True
    
    async def mark_server_as_couldnt_join(self, server_ip) -> bool:
        server = server_ip.split(":")[0]
        port = server_ip.split(":")[1]
        # return false if no such server exists
        if not await self.is_server_seen(server, port):
            return False
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE servers SET sorted_tag = "user_couldnt_join" WHERE server_ip = ? AND port = ?', (server, port))
            await db.commit()
        return True

