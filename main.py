import nextcord
from cogs.Admin import AdminCommands
from cogs.Moderation import ModerationCommands
from cogs.Listeners import Listeners
from cogs.Democracy import DemocracyCommands
from cogs.General import GeneralCommands
from cogs.Routines import Routines
from cogs.Automata import Automata
from db.CraftprobeDb import CraftprobeDb
from db.Db import Db
from cogs.Craftprobe import Craftprobe
from utils.Language import Language
from utils.AI import AI
from Config import Config
from Context import Context
from db.CsDb import CsDb

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
ai: AI = AI(db, config)
csdb = CsDb(config)
craftprobe_db: CraftprobeDb = CraftprobeDb(config)
context: Context = Context(client, db, craftprobe_db, config, language, ai, csdb)


client.add_cog(AdminCommands(context))
client.add_cog(ModerationCommands(context))
client.add_cog(DemocracyCommands(context))
client.add_cog(Listeners(context))
client.add_cog(GeneralCommands(context))
client.add_cog(Routines(context))
client.add_cog(Craftprobe(context))
client.add_cog(Automata(context))

client.run(open("token.txt", 'r').readline().replace("\n", ""))