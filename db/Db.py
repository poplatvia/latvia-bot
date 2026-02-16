import aiosqlite

class Db:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Python workaround to make a singleton."""
        if cls._instance is None:
            cls._instance = super(Db, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_name="main.db"):
        self.db_name = db_name

    async def initialize(self):
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

            await db.commit()

    # -------------- CSV -------------- #
    async def to_CSV(self):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT user_id, channel_id, message_content FROM messages WHERE message_content is not null')
            row = await cursor.fetchall()
            return row

    # -------------- Moderation -------------- #

    async def add_warning(self, user, reason, issuer_id):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT INTO warnings (user_id, reason, issuer)
                VALUES (?, ?, ?)
            ''', (str(user), reason, str(issuer_id)))
            await db.commit()

    async def get_warnings(self, user):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT reason, issuer, created_at FROM warnings WHERE user_id = ?', (str(user),))
            row = await cursor.fetchall()
            return row

    # -------------- User Statistics -------------- #

    async def add_message(self, user_id, channel_id, message_content):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT INTO messages (user_id, channel_id, message_content)
                VALUES (?, ?, ?)
            ''', (str(user_id), str(channel_id), message_content))
            await db.commit()

    async def add_reaction(self, message_id, user_id, reaction_emoji, add_or_remove):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT INTO reactions (message_id, user_id, reaction_emoji, add_or_remove)
                VALUES (?, ?, ?, ?)
            ''', (str(message_id), str(user_id), reaction_emoji, add_or_remove))
            await db.commit()
        
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