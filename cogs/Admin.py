import nextcord
from nextcord.ext import commands
import sys
from db.Db import Db

class AdminCommands(commands.Cog):
    def __init__(self, bot, db, config):
        self.bot = bot
        self.db = db
        
        self.conf = config

    @nextcord.slash_command(name="shutdown", description="(Admin command) Turn off the bot")
    async def shutdown(self, ctx):
        if ctx.user.id in self.conf.config["admins"]:
            await ctx.send("Shutting down!")
            sys.exit(0)

    @nextcord.slash_command(name="csv", description="(Admin command) Export data.")
    async def csv(self, ctx):
        if ctx.user.id not in self.conf.config["admins"]:
            await ctx.response.send_message("Admins only.", ephemeral=True)
        
        await ctx.response.send_message("Not implemented.", ephemeral=True)

    @nextcord.slash_command(name="start", description="(Admin command) Start the database if discord is being weird.")
    async def manual_db_start(self, ctx):
        if ctx.user.id in self.conf.config["admins"]:
            await self.db.initialize()
            await ctx.send("Started.")

    @nextcord.slash_command(name="sql", description="(Admin command) Mess with DB.")
    async def sql(self, ctx, query: str):
        if ctx.user.id not in self.conf.config["admins"]:
            await ctx.response.send_message("Admins only.", ephemeral=True)
        
        try:
            result = await self.db.raw_sql(query)
            await ctx.response.send_message(f"Query executed successfully. Result: {result}", ephemeral=True)
        except Exception as e:
            await ctx.response.send_message(f"Error executing query: {e}", ephemeral=True)

    @nextcord.slash_command(name="generate_leaderboard", description="(Admin command) Generate leaderboard.")
    async def generate_leaderboard(self, ctx):
        if ctx.user.id not in self.conf.config["admins"]:
            await ctx.response.send_message("Admins only.", ephemeral=True)
        
        await self.db.generate_leaderboard()
        await ctx.response.send_message("Leaderboard generated.", ephemeral=True)

    @nextcord.slash_command(name="config", description="Different config commands.")
    async def config(self, ctx: nextcord.Interaction):
        pass

    @config.subcommand(name="set", description="Set elo config.")
    async def config_elo_set(self, ctx: nextcord.Interaction):
        pass

    @config_elo_set.subcommand(name="warning", description="Set warning multiplier.")
    async def config_elo_set_warning(self, ctx: nextcord.Interaction, multiplier: float):
        if ctx.user.id not in self.conf.config["admins"]:
            await ctx.response.send_message("Admins only.", ephemeral=True)
        
        self.conf.config["elo"]["warning_multiplier"] = multiplier
        self.conf.write_config()
        await ctx.response.send_message(f"Warning multiplier set to {multiplier}.", ephemeral=True)

    @config_elo_set.subcommand(name="curse", description="Set curse word multiplier.")
    async def config_elo_set_curse(self, ctx: nextcord.Interaction, multiplier: float):
        if ctx.user.id not in self.conf.config["admins"]:
            await ctx.response.send_message("Admins only.", ephemeral=True)
        
        self.conf.config["elo"]["curse_multiplier"] = multiplier
        self.conf.write_config()
        await ctx.response.send_message(f"Curse word multiplier set to {multiplier}.", ephemeral=True)

    @config_elo_set.subcommand(name="slur", description="Set slur multiplier.")
    async def config_elo_set_slur(self, ctx: nextcord.Interaction, multiplier: float):
        if ctx.user.id not in self.conf.config["admins"]:
            await ctx.response.send_message("Admins only.", ephemeral=True)
        
        self.conf.config["elo"]["slur_multiplier"] = multiplier
        self.conf.write_config()
        await ctx.response.send_message(f"Slur multiplier set to {multiplier}.", ephemeral=True)
    
    @config_elo_set.subcommand(name="spam", description="Set spam multiplier.")
    async def config_elo_set_spam(self, ctx: nextcord.Interaction, multiplier: float):
        if ctx.user.id not in self.conf.config["admins"]:
            await ctx.response.send_message("Admins only.", ephemeral=True)
        
        self.conf.config["elo"]["spam_multiplier"] = multiplier
        self.conf.write_config()
        await ctx.response.send_message(f"Spam multiplier set to {multiplier}.", ephemeral=True)

    @nextcord.slash_command(name="backup", description="(Admin command) Backup the database")
    async def backup(self, ctx):
        if ctx.user.id not in self.conf.config["admins"]:
            await ctx.response.send_message("Admins only.", ephemeral=True)
            return
        channel = self.bot.get_channel(1473601956730634321)
        await channel.send(file=nextcord.File('main.db'))
        await ctx.response.send_message("Database backed up.", ephemeral=True)

    @config.subcommand(name="reset", description="(Admin command) Reset the config to default.")
    async def config_reset(self, ctx):
        if ctx.user.id not in self.conf.config["admins"]:
            await ctx.response.send_message("Admins only.", ephemeral=True)
            return
        self.conf.reset_config()
        await ctx.response.send_message("Config reset to default.", ephemeral=True)