import nextcord
from cogs.Admin import AdminCommands
from cogs.Moderation import ModerationCommands
from cogs.Listeners import Listeners
from cogs.Democracy import DemocracyCommands
from db.Db import Db
from utils.Language import Language
from cogs.General import GeneralCommands

intents = nextcord.Intents.all()
intents.message_content = True
intents.reactions = True
intents.voice_states = True
intents.bans = True
intents.members = True

client = nextcord.ext.commands.Bot(command_prefix="null", intents=intents)

language: Language = Language()
db: Db = Db(language)
admins: list[int] = [1330980258253635594]

client.add_cog(AdminCommands(client, db, admins))
client.add_cog(ModerationCommands(client, db, admins))
client.add_cog(DemocracyCommands(client, db, admins))
client.add_cog(Listeners(client, db, language))
client.add_cog(GeneralCommands(client, db))

client.run(open("token.txt", 'r').readline().replace("\n", ""))