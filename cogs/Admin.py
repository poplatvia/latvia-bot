import nextcord
from nextcord.ext import commands
import sys
from db.Db import Db

class AdminCommands(commands.Cog):
    def __init__(self, bot, db, admins: list[int]):
        self.bot = bot
        self.db = db
        
        self.admins = admins

    @nextcord.slash_command(name="shutdown", description="(Admin command) Turn off the bot")
    async def shutdown(self, ctx):
        if ctx.user.id in self.admins:
            await ctx.send("Shutting down!")
            sys.exit(0)

    @nextcord.slash_command(name="csv", description="(Admin command) Export data.")
    async def csv(self, ctx):
        if ctx.user.id not in self.admins:
            await ctx.response.send_message("Admins only.", ephemeral=True)
        
        await ctx.response.send_message("Not implemented.", ephemeral=True)

    @nextcord.slash_command(name="start", description="(Admin command) Start the database if discord is being weird.")
    async def manual_db_start(self, ctx):
        if ctx.user.id in self.admins or ctx.user.id == 843958503324123144:
            await self.db.initialize()
            await ctx.send("Started.")