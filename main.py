import nextcord
from cogs.Admin import AdminCommands
from cogs.Moderation import ModerationCommands
from cogs.Listeners import Listeners
from db.Db import Db

intents = nextcord.Intents.all()
intents.message_content = True
intents.reactions = True
intents.voice_states = True
intents.bans = True
intents.members = True

client = nextcord.ext.commands.Bot(command_prefix="null", intents=intents)

db: Db = Db()
admins: list[int] = [1330980258253635594]

client.add_cog(AdminCommands(client, db, admins))
client.add_cog(ModerationCommands(client, db, admins))
client.add_cog(Listeners(client, db))

client.run(open("token.txt", 'r').readline().replace("\n", ""))