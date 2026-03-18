import nextcord
from nextcord.ext import commands
import sys
from db.Db import Db
from checks import bot_channel_only

class GeneralCommands(commands.Cog):
    def __init__(self, context):
        self.bot = context.client
        self.db = context.db
        self.config = context.config

    # Prevents ugly errors from printing
    # async def cog_application_command_error(self, interaction: nextcord.Interaction, error):
    #     if isinstance(error, nextcord.errors.ApplicationCheckFailure):
    #         pass

    @nextcord.slash_command(name="elo", description="Calculate a user's elo.")
    @bot_channel_only()
    async def elo(self, ctx, user: nextcord.User):
        elo = await self.db.calculate_elo(user.id)
        await ctx.send(f"{user.mention}'s elo is {elo}")

    @nextcord.slash_command(name="spam", description="Number of times a user has spammed.")
    @bot_channel_only()
    async def spam(self, ctx, user: nextcord.User):
        count = await self.db.number_of_spams(user.id)
        await ctx.send(f"{user.mention} has spammed {count} times.")

    @nextcord.slash_command(name="warning", description="Various warning-related commands.")
    @bot_channel_only()
    async def warning(self, ctx):
        pass

    @warning.subcommand(name="top", description="Show the top 10 users with the most warnings.")
    async def top(self, ctx):
        top_warnings = await self.db.get_top_warnings()
        if not top_warnings:
            await ctx.send("No warnings found.")
            return
    
        embed = nextcord.Embed(title="🚫 Top 10 Users with Most Warnings 🚫", color=nextcord.Color.red())
        for user_id, count in top_warnings:
            user = self.bot.get_user(user_id)
            username = user.name if user else f"User ID {user_id}"
            embed.add_field(name=f"{username}", value=f"{count} warning(s)", inline=False)

        await ctx.send(embed=embed)

    @warning.subcommand(name="count", description="Count warnings for a user.")
    async def count(self, ctx, user: nextcord.User):
        warnings = await self.db.get_warnings(user.id)
        if not warnings:
            await ctx.send(f"{user.mention} has no warnings.")
            return
        
        reasons_str = ""
        count = 0
        for warning in warnings:
            reason = warning[0]
            reasons_str += "- " + reason + "\n"
            count += 1
            if count >= 10:
                reasons_str += f"... and {len(warnings) - count} more."
                break
        
        await ctx.send(f"{user.mention} has {len(warnings)} warning(s).\n{reasons_str}")

    @nextcord.slash_command(name="curse", description="Various curse-related commands.")
    @bot_channel_only()
    async def curse(self, ctx):
        pass

    @curse.subcommand(name="count", description="Count curse words for a user.")
    async def count(self, ctx, user: nextcord.User):
        curse_count, slur_count = await self.db.get_curse_count(user.id)
        await ctx.send(f"{user.mention} has used {curse_count} curse word(s) and {slur_count} slur(s).")

    @curse.subcommand(name="top", description="Show the top 10 users with the most curse words.")
    async def top(self, ctx):
        top_curses = await self.db.get_top_curse_users()
        if not top_curses:
            await ctx.send("No curse words found.")
            return
    
        embed = nextcord.Embed(title="Top 10 Users with Most Curse Words", color=nextcord.Color.dark_red())
        for user_id, curse_count, slur_count in top_curses:
            user = self.bot.get_user(user_id)
            username = user.name if user else f"User ID {user_id}"
            embed.add_field(name=f"{username}", value=f"{curse_count} curse word(s) and {slur_count} slur(s)", inline=False)

        await ctx.send(embed=embed)

    @nextcord.slash_command(name="leaderboard", description="Show the elo leaderboard.")
    @bot_channel_only()
    async def leaderboard(self, ctx):
        leaderboard: dict[str, float] = await self.db.get_leaderboard(allow_min_or_max_elo=False)
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

