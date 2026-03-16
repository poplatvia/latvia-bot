from typing import Tuple

import aiosqlite
from datetime import datetime, timedelta
import math

class CsDb:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Python workaround to make a singleton."""
        if cls._instance is None:
            cls._instance = super(CsDb, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config, db_name="cs.db") -> None:
        self.config = config
        self.db_name = db_name

        # check db exists
        try:
            with open(db_name, 'r') as f:
                pass
        except FileNotFoundError:
            raise Exception(f"Computer science database not found.")


    async def initialize(self) -> None:
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                '''
                CREATE TABLE IF NOT EXISTS dfa (
                    user_id INT NOT NULL PRIMARY KEY,
                    alphabet VARCHAR(255) NOT NULL,
                    start_state INT
                );
                '''
            )

            await db.execute(
                '''
                CREATE TABLE IF NOT EXISTS states (
                    user_id INT NOT NULL,
                    state_id INT NOT NULL,
                    is_accepting BOOLEAN NOT NULL,
                    PRIMARY KEY (user_id, state_id),
                    FOREIGN KEY (user_id) REFERENCES dfa(user_id) ON DELETE CASCADE
                );
                '''
            )

            await db.execute(
                '''
                CREATE TABLE IF NOT EXISTS transitions (
                    user_id INT NOT NULL,
                    src_state_id INT NOT NULL,
                    input_symbol VARCHAR(255) NOT NULL,
                    dst_state_id INT NOT NULL,
                    PRIMARY KEY (user_id, src_state_id, input_symbol, dst_state_id),
                    FOREIGN KEY (user_id) REFERENCES dfa(user_id) ON DELETE CASCADE
                );
                '''
            )

            await db.commit()

    async def add_dfa(self, user_id: int, alphabet: str) -> None:
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute(
                '''
                INSERT INTO dfa (user_id, alphabet)
                VALUES (?, ?)
                ''',
                (user_id, alphabet)
            )
            await db.commit()
        
    async def add_state(self, user_id: int, state_id: int, is_accepting: bool) -> None:
        async with aiosqlite.connect(self.db_name) as db:
            # insert state or update is_accepting if state already exists
            await db.execute(
                '''
                INSERT INTO states (user_id, state_id, is_accepting)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, state_id) DO UPDATE SET is_accepting=excluded.is_accepting
                ''',
                (user_id, state_id, is_accepting)
            )
            await db.commit()

    async def add_transition(self, user_id: int, src_state_id: int, input_symbol: str, dst_state_id: int) -> None:
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                '''
                INSERT INTO transitions (user_id, src_state_id, input_symbol, dst_state_id)
                VALUES (?, ?, ?, ?)
                ''',
                (user_id, src_state_id, input_symbol, dst_state_id)
            )
            await db.commit()
    
    async def set_start_state(self, user_id: int, start_state: int) -> None:
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                '''
                UPDATE dfa
                SET start_state = ?
                WHERE user_id = ?
                ''',
                (start_state, user_id)
            )
            await db.commit()

    async def get_dfa_alphabet(self, user_id: int) -> str:
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute(
                '''
                SELECT alphabet
                FROM dfa
                WHERE user_id = ?
                ''',
                (user_id,)
            )
            row = await cursor.fetchone()
            return row[0] if row else None
    
    async def get_dfa_start_state(self, user_id: int) -> int:
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute(
                '''
                SELECT start_state
                FROM dfa
                WHERE user_id = ?
                ''',
                (user_id,)
            )
            row = await cursor.fetchone()
            return row[0] if row else None
        
    async def get_dfa_states(self, user_id: int) -> list[dict]:
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute(
                '''
                SELECT state_id, is_accepting
                FROM states
                WHERE user_id = ?
                ''',
                (user_id,)
            )
            rows = await cursor.fetchall()
            return [{'state_id': row[0], 'is_accepting': bool(row[1])} for row in rows]
        
    async def get_dfa_transitions(self, user_id: int) -> list[dict]:
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute(
                '''
                SELECT src_state_id, input_symbol, dst_state_id
                FROM transitions
                WHERE user_id = ?
                ''',
                (user_id,)
            )
            rows = await cursor.fetchall()
            return [{'from_state': row[0], 'input_symbol': row[1], 'to_state': row[2]} for row in rows]
        
    async def reset_dfa(self, user_id: int) -> None:
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                '''
                DELETE FROM states
                WHERE user_id = ?
                ''',
                (user_id,)
            )
            await db.execute(
                '''
                DELETE FROM transitions
                WHERE user_id = ?
                ''',
                (user_id,)
            )
            await db.execute(
                '''
                DELETE FROM dfa
                WHERE user_id = ?
                ''',
                (user_id,)
            )
            await db.commit()