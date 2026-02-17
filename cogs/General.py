import nextcord
from nextcord.ext import commands
import sys
from db.Db import Db

class GeneralCommands(commands.Cog):
    def __init__(self, bot, db, config):
        self.bot = bot
        self.db = db
        self.config = config

    @nextcord.slash_command(name="elo", description="Calculate a user's elo.")
    async def elo(self, ctx, user: nextcord.User):
        elo = await self.db.calculate_elo(user.id)
        await ctx.send(f"{user.mention}'s elo is {elo}")

    @nextcord.slash_command(name="spam", description="Number of times a user has spammed.")
    async def spam(self, ctx, user: nextcord.User):
        count = await self.db.number_of_spams(user.id)
        await ctx.send(f"{user.mention} has spammed {count} times.")

    @nextcord.slash_command(name="leaderboard", description="Show the elo leaderboard.")
    async def leaderboard(self, ctx):

        leaderboard = await self.db.get_leaderboard()
        if not leaderboard:
            await ctx.send("Leaderboard is empty.")
            return
        
        # sort leaderboard by elo in descending order
        leaderboard = dict(sorted(leaderboard.items(), key=lambda item: item[1], reverse=True))
        
        embed = nextcord.Embed(title="🏆 Elo Leaderboard 🏆", color=nextcord.Color.gold())
        halfway_point = len(leaderboard) // 2
        count = 0
        for user_id, elo in leaderboard.items():
            if count == halfway_point:
                embed.add_field(name="...", value="", inline=False)
            user = self.bot.get_user(user_id)
            username = user.name if user else f"User ID {user_id}"
            embed.add_field(name=f"{username}", value=f"{elo} ELO points.", inline=False)
            count += 1

        await ctx.send(embed=embed)

