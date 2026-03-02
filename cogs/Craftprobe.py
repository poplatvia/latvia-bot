import nextcord
from nextcord.ext import commands
from db.CraftprobeDb import CraftprobeDb
from checks import bot_channel_only

class Craftprobe(commands.Cog):
    def __init__(self, bot, db: CraftprobeDb, config):
        self.bot = bot
        self.db = db
        self.config = config

    @nextcord.slash_command(name="craftprobe", description="Various craftprobe commands.")
    @bot_channel_only()
    async def craftprobe(self, ctx):
        pass

    @craftprobe.subcommand(name="seen", description="Check if a player has been seen on the server.")
    async def seen(self, ctx):
        pass

    @seen.subcommand(name="player", description="Check if player has been seen.")
    async def player(self, ctx: nextcord.Interaction, username: str):
        await ctx.response.defer()
        seen = await self.db.is_player_seen(username)
        if seen:
            await ctx.followup.send(f"✅ Player {username} is in the database.")
        else:
            await ctx.followup.send(f"❌ Player {username} is not in the database.")

    @seen.subcommand(name="server", description="Check if server has been seen.")
    async def server(self, ctx: nextcord.Interaction, server_ip: str):
        await ctx.response.defer(ephemeral=True)
        seen = await self.db.is_server_seen(server_ip)
        if seen:
            await ctx.followup.send(f"✅ Server {server_ip} is in the database.")
        else:
            await ctx.followup.send(f"❌ Server {server_ip} is not in the database.")

    @craftprobe.subcommand(name="preprocess", description="Preprocess the database. This will remove all invalid minecraft usernames.")
    async def preprocess(self, ctx):
        if ctx.user.id not in self.config.config["admins"]:
            await ctx.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return
        
        await ctx.response.defer(ephemeral=True)
        await self.db.preprocess()
        await ctx.followup.send("✅ Database preprocessed.")

