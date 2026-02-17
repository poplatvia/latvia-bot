import nextcord
from cogs.Admin import AdminCommands
from cogs.Moderation import ModerationCommands
from cogs.Listeners import Listeners
from cogs.Democracy import DemocracyCommands
from cogs.General import GeneralCommands
from cogs.Routines import Routines
from db.Db import Db
from utils.Language import Language
from Config import Config

intents = nextcord.Intents.all()
intents.message_content = True
intents.reactions = True
intents.voice_states = True
intents.bans = True
intents.members = True

client = nextcord.ext.commands.Bot(command_prefix="null", intents=intents)

config = Config()

language: Language = Language()
db: Db = Db(language, config)

client.add_cog(AdminCommands(client, db, config))
client.add_cog(ModerationCommands(client, db, config))
client.add_cog(DemocracyCommands(client, db, config))
client.add_cog(Listeners(client, db, language, config))
client.add_cog(GeneralCommands(client, db, config))
client.add_cog(Routines(client, db, config))

client.run(open("token.txt", 'r').readline().replace("\n", ""))