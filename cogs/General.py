import nextcord
from nextcord.ext import commands
import sys
from db.Db import Db

class GeneralCommands(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    @nextcord.slash_command(name="elo", description="Calculate a user's elo.")
    async def elo(self, ctx, user: nextcord.User):
        elo = await self.db.calculate_elo(user.id)
        await ctx.send(f"{user.mention}'s elo is {elo}")

    @nextcord.slash_command(name="spam", description="Number of times a user has spammed.")
    async def spam(self, ctx, user: nextcord.User):
        count = await self.db.number_of_spams(user.id)
        await ctx.send(f"{user.mention} has spammed {count} times.")

