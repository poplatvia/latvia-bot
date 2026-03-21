from typing import Tuple

import aiosqlite
from datetime import datetime, timedelta
import random

class CraftprobeDb:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Python workaround to make a singleton."""
        if cls._instance is None:
            cls._instance = super(CraftprobeDb, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config, main_db_name: str, db_name="db.sqlite3") -> None:
        self.config = config
        self.db = main_db_name
        self.db_name = db_name
        self.union_servers = set()

        # check db exists
        try:
            with open(db_name, 'r') as f:
                pass
        except FileNotFoundError:
            raise Exception(f"Craftprobe database not found.")
        
    # preprocessing. Remove all invalid minecraft usernames.
    async def preprocess(self):
        async with aiosqlite.connect(self.db_name) as db:
            # delete all servers with players seen who have invalid usernames. This is necessary because the players_seen table has a foreign key constraint on the playername_uuid table.
            await db.execute('DELETE FROM servers WHERE concat(server_ip, ":", port) IN (SELECT server FROM players_seen WHERE player_uuid IN (SELECT player_uuid FROM playername_uuid WHERE player_name NOT GLOB "[a-zA-Z0-9_]*" or length(player_name) < 3 or length(player_name) > 16))')
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
        
    async def get_random_server(self, version: str = None) -> str | None:
        async with aiosqlite.connect(self.db_name) as db:
            tagged_servers: set[str] = set()
            async with aiosqlite.connect(self.db) as bot_db:
                cursor = await bot_db.execute('SELECT server_ip, port FROM tagged_servers')
                rows = await cursor.fetchall()
                tagged_servers = {f"{row[0]}:{row[1]}" for row in rows}

            if len(self.union_servers) < 10:
                cursor = await db.execute('SELECT server FROM players_seen')
                rows = await cursor.fetchall()
                # add port 25565 to all servers without a port.
                set_servers1: set[str] = {row[0] if ':' in row[0] else f"{row[0]}:25565" for row in rows}

                cursor = await db.execute('SELECT (server_ip || ":" || port), server_version FROM servers')
                rows = await cursor.fetchall()
                dict_servers2: dict[str, str] = {row[0]: row[1] for row in rows}

                for s in dict_servers2:
                    if s in set_servers1:
                        self.union_servers.add(s)

            # print(f"Unique servers in players_seen and servers: {len(self.union_servers)}")
            # print(f"Head of union servers: {list(self.union_servers)[:10]}")

            if version:
                server = random.choice([s for s in self.union_servers if dict_servers2.get(s) == version and s not in tagged_servers]) if len(self.union_servers) > 0 else None
            else:
                server = random.choice([s for s in self.union_servers if s not in tagged_servers]) if len(self.union_servers) > 0 else None
            # remove the server from the union servers set to avoid repeats in the future.
            if server:
                self.union_servers.remove(server)
            return server
            

    
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
    
    async def get_number_of_servers_with_version(self, version) -> int:
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT COUNT(*) FROM servers where server_version = ?', (version,))
            row = await cursor.fetchall()
            return row[0][0]
        
    async def get_number_of_players(self) -> int:
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT COUNT(DISTINCT player_uuid) FROM playername_uuid')
            row = await cursor.fetchone()
            return row[0]
        
    async def get_number_of_servers(self) -> int:
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT COUNT(*) FROM servers')
            row = await cursor.fetchone()
            return row[0]
        
    async def get_players_with_most_entries_in_players_seen(self) -> list[Tuple[str, int]]:
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT player_name, COUNT(*) as count FROM playername_uuid JOIN players_seen ON playername_uuid.player_uuid = players_seen.player_uuid GROUP BY playername_uuid.player_uuid ORDER BY count DESC LIMIT 10')
            row = await cursor.fetchall()
            return [(row[i][0], row[i][1]) for i in range(len(row))]
        
    async def get_likely_server_hosting_ips(self) -> list[Tuple[str, int]]:
        # finds all servers with more than 50 server_ip entries with a different port.
        # multiple ports with the same server_ip is a strong indicator of a hosting provider.
        # Select random 10 of these hosting provider IPs and return them with the number of different ports they have in the database.
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT server_ip, COUNT(DISTINCT port) as count FROM servers GROUP BY server_ip HAVING count > 50 ORDER BY RANDOM() DESC LIMIT 10')
            row = await cursor.fetchall()
            return [(row[i][0], row[i][1]) for i in range(len(row))]

