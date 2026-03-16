from nextcord.ext import commands
from nextcord.ext import commands, tasks

class Routines(commands.Cog):
    def __init__(self, context):
        self.bot = context.client
        self.db = context.db
        self.config = context.config

        self.leaderboard_task.start()

    @tasks.loop(seconds=600)
    async def leaderboard_task(self):
        print("Generating leaderboard...")
        await self.db.generate_leaderboard()

    @leaderboard_task.before_loop
    async def before_leaderboard_task(self):
        await self.bot.wait_until_ready()

    async def cog_unload(self):
        await self.db.close()
