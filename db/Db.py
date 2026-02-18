import aiosqlite
from datetime import datetime, timedelta

class Db:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Python workaround to make a singleton."""
        if cls._instance is None:
            cls._instance = super(Db, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, language, config, db_name="main.db") -> None:
        self.language = language
        self.config = config
        self.db_name = db_name

    async def initialize(self) -> None:
        """Initialize the database by creating the necessary tables."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                '''
                CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                channel_id INTEGER,
                message_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                '''
            )

            await db.execute(
                '''
                CREATE TABLE IF NOT EXISTS reactions (
                id INTEGER PRIMARY KEY,
                message_id TEXT,
                user_id INTEGER,
                reaction_emoji TEXT,
                add_or_remove TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                '''
            )
            
            await db.execute(
                '''
                CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                reason TEXT,
                issuer INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                '''
            )

            await db.execute(
                '''
                CREATE TABLE IF NOT EXISTS votekicks (
                id INTEGER PRIMARY KEY,
                target_user_id INTEGER,
                started_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                '''
            )

            await db.execute(
                '''
                CREATE TABLE IF NOT EXISTS leaderboard (
                user_id INTEGER PRIMARY KEY,
                elo REAL
                );
                '''
            )

            await db.commit()

    async def generate_leaderboard(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('DELETE FROM leaderboard')
            cursor = await db.execute('SELECT DISTINCT user_id FROM messages')
            row = await cursor.fetchall()
            for user in row:
                user_id = user[0]
                elo = await self.calculate_elo(user_id)
                await db.execute('INSERT INTO leaderboard (user_id, elo) VALUES (?, ?)', (str(user_id), elo))
            await db.commit()

    async def get_leaderboard(self, n=5, allow_min_or_max_elo=True):
        async with aiosqlite.connect(self.db_name) as db:
            user_elo: dict = {}
            for label in ["ASC", "DESC"]:
                if not allow_min_or_max_elo:
                    cursor = await db.execute(f'SELECT user_id, elo FROM leaderboard WHERE elo > 0 AND elo < 100 ORDER BY elo {label} LIMIT ?', (n,))
                else:
                    cursor = await db.execute(f'SELECT user_id, elo FROM leaderboard ORDER BY elo {label} LIMIT ?', (n,))
                row = await cursor.fetchall()
                for user in row:
                    user_id = user[0]
                    elo = user[1]
                    user_elo[user_id] = elo
            return user_elo

    # -------------- CSV -------------- #
    async def to_CSV(self):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT user_id, channel_id, message_content FROM messages WHERE message_content is not null')
            row = await cursor.fetchall()
            return row

    # -------------- Moderation -------------- #

    async def add_warning(self, user, reason, issuer_id) -> None:
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT INTO warnings (user_id, reason, issuer)
                VALUES (?, ?, ?)
            ''', (str(user), reason, str(issuer_id)))
            await db.commit()

    async def get_number_of_warnings(self, user) -> int:
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT COUNT(*) FROM warnings WHERE user_id = ?', (str(user),))
            row = await cursor.fetchone()
            return int(row[0]) if row else 0

    async def get_warnings(self, user):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT reason, issuer, created_at FROM warnings WHERE user_id = ?', (str(user),))
            row = await cursor.fetchall()
            return row

    # -------------- User Statistics -------------- #

    async def add_message(self, message_id, user_id, channel_id, message_content: str):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT INTO messages (message_id, user_id, channel_id, message_content)
                VALUES (?, ?, ?, ?)
            ''', (str(message_id), str(user_id), str(channel_id), message_content))
            await db.commit()

    async def add_reaction(self, message_id, user_id, reaction_emoji, add_or_remove: str):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT INTO reactions (message_id, user_id, reaction_emoji, add_or_remove)
                VALUES (?, ?, ?, ?)
            ''', (str(message_id), str(user_id), reaction_emoji, add_or_remove))
            await db.commit()

    # -------------- Votekick -------------- #
    async def add_votekick(self, target_user_id, started_by):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT INTO votekicks (target_user_id, started_by)
                VALUES (?, ?)
            ''', (str(target_user_id), str(started_by)))
            await db.commit()

    # -------------- Elo -------------- #
    async def calculate_elo(self, user_id):
        """
        User's elo is calculated based on the number of messages, 
        the number of curse words, and the number of warnings. The 
        more messages and the fewer curse words/warnings, the higher the elo.
        """
        # x = number of chars in a message
        # y = number of curses in a message
        curse_calc = lambda x, y, z: max(0, 100*(1-((self.config.config["elo"]["curse_multiplier"]*y + self.config.config["elo"]["slur_multiplier"]*z)/x)))
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT message_content FROM messages WHERE user_id = ?', (str(user_id),))
            row = await cursor.fetchall()
            elo = 0
            count = 0
            for message in row:
                message_content = message[0]
                if len(message_content) == 0:
                    continue
                
                num_curses = self.language.number_of_curse_words(message_content)
                num_really_bad_curses = self.language.number_of_really_bad_curse_words(message_content)
                count += 1
                elo += curse_calc(len(message_content), num_curses, num_really_bad_curses)

            if count == 0:
                return 0
            
            elo_avg = elo / count

            num_spams = await self.number_of_spams(user_id)
            # 1 spam every 100 messages allowed
            if num_spams > 0:
                num_messages_between_spams = count / max(1, num_spams)
                # Linear penalty because before there were crazy drop offs
                spam_ratio = min(1.0, num_messages_between_spams / 100)
                spam_penalty = max(0.1, 1.0 - (1.0 - spam_ratio) * self.config.config["elo"]["spam_multiplier"])
                elo_avg *= spam_penalty

            num_warnings = await self.get_number_of_warnings(user_id)
            warning_penalty = num_warnings * self.config.config["elo"]["warning_multiplier"]
            elo_avg = max(0, elo_avg - warning_penalty)

            return round(elo_avg, 2)
        
    async def time_since_first_message(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT created_at FROM messages WHERE user_id = ? ORDER BY created_at ASC LIMIT 1', (str(user_id),))
            row = await cursor.fetchone()
            if row is None:
                return datetime.now() - datetime.now()  # If user has no messages, return 0 time
            first_message_time = row[0]
            first_message_time = datetime.strptime(first_message_time, "%Y-%m-%d %H:%M:%S")
            return datetime.now() - first_message_time

    async def number_of_spams(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            # Introduction to databases nightmare query flashback
            cursor = await db.execute("""
                SELECT COUNT(*) AS spam_instances
                FROM (
                    SELECT
                        created_at,
                        LAG(created_at) OVER (
                            PARTITION BY user_id
                            ORDER BY created_at
                        ) AS prev_created_at
                    FROM messages
                    WHERE user_id = ?
                )
                WHERE prev_created_at IS NOT NULL
                    AND ABS(strftime('%s', created_at) - strftime('%s', prev_created_at)) <= 1;
            """, (user_id,))
            
            row = await cursor.fetchone()
            return int(row[0]) if row else 0


    # --- DB migration n shiet --- #    
    async def raw_sql(self, string):
        async with aiosqlite.connect(self.db_name) as db:
            if "select" in string.lower():
                cursor = await db.execute(string)
                row = await cursor.fetchall()
                message = ""
                for item in row:
                    message += str(item) + "\n"
                return message
            else:
                await db.execute(string)
                await db.commit()
                return None