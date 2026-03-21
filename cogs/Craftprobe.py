import nextcord
from nextcord.ext import commands
from db.CraftprobeDb import CraftprobeDb
from checks import bot_channel_only, scan_channel_only
from typing import Tuple

class Craftprobe(commands.Cog):
    def __init__(self, context):
        self.bot = context.client
        self.craftprobe_db = context.craftprobe_db
        self.db = context.db
        self.config = context.config

    @nextcord.slash_command(name="craftprobe", description="Various craftprobe commands.")
    async def craftprobe(self, ctx):
        pass

    @craftprobe.subcommand(name="get", description="Get various information from the database.")
    @scan_channel_only()
    async def get(self, ctx):
        pass

    @craftprobe.subcommand(name="whitelist", description="Set a server as whitelisted.")
    @scan_channel_only()
    async def whitelist(self, ctx, server: str):
        elo = await self.db.calculate_elo(ctx.user.id)
        if elo < 25 or elo is None:
            await ctx.response.send_message("Your Elo is too low to use this command.", ephemeral=True)
            return
        await ctx.response.defer(ephemeral=True)
        success = await self.craftprobe_db.mark_server_as_whitelisted(server)
        if success:
            await self.db.insert_whitelisted_server(server, ctx.user.id)
            await ctx.followup.send(f"✅ Server {server} has been whitelisted.")
        else:
            await ctx.followup.send(f"❌ Server {server} is not in the database.")

    @craftprobe.subcommand(name="hub", description="Set a server as a hub.")
    @scan_channel_only()
    async def hub(self, ctx, server: str):
        elo = await self.db.calculate_elo(ctx.user.id)
        if elo < 25 or elo is None:
            await ctx.response.send_message("Your Elo is too low to use this command.", ephemeral=True)
            return
        await ctx.response.defer(ephemeral=True)
        success = await self.craftprobe_db.mark_server_as_hub(server)
        if success:
            await self.db.insert_tagged_server(server, ctx.user.id, "hub")
            await ctx.followup.send(f"✅ Server {server} has been marked as a hub.", ephemeral=True)
        else:
            await ctx.followup.send(f"❌ Server {server} is not in the database.", ephemeral=True)

    @craftprobe.subcommand(name="modded", description="Set a server as modded.")
    @scan_channel_only()
    async def modded(self, ctx, server: str):
        elo = await self.db.calculate_elo(ctx.user.id)
        if elo < 25 or elo is None:
            await ctx.response.send_message("Your Elo is too low to use this command.", ephemeral=True)
            return
        await ctx.response.defer(ephemeral=True)
        success = await self.craftprobe_db.mark_server_as_modded(server)
        if success:
            await self.db.insert_tagged_server(server, ctx.user.id, "modded")
            await ctx.followup.send(f"✅ Server {server} has been marked as modded.", ephemeral=True)
        else:
            await ctx.followup.send(f"❌ Server {server} is not in the database.", ephemeral=True)

    @craftprobe.subcommand(name="couldnt_join", description="Set a server as couldn't join.")
    @scan_channel_only()
    async def couldnt_join(self, ctx, server: str):
        elo = await self.db.calculate_elo(ctx.user.id)
        if elo < 25 or elo is None:
            await ctx.response.send_message("Your Elo is too low to use this command.", ephemeral=True)
            return
        await ctx.response.defer(ephemeral=True)
        success = await self.craftprobe_db.mark_server_as_couldnt_join(server)
        if success:
            await self.db.insert_tagged_server(server, ctx.user.id, "couldnt_join")
            await ctx.followup.send(f"✅ Server {server} has been marked as couldn't join.", ephemeral=True)
        else:
            await ctx.followup.send(f"❌ Server {server} is not in the database.", ephemeral=True)

    @get.subcommand(name="rserver", description="Get a random server.")
    async def rserver(self, ctx, version: str=None):
        elo = await self.db.calculate_elo(ctx.user.id)
        if elo < 25 or elo is None:
            await ctx.response.send_message("Your Elo is too low to use this command.", ephemeral=True)
            return
        
        await ctx.response.defer(ephemeral=True)
        server = await self.craftprobe_db.get_random_server(version)
        if server:
            await self.db.insert_fetched_server(server, ctx.user.id)
            await ctx.followup.send(f"{server}", ephemeral=True)
        else:
            await ctx.followup.send("No servers found in the database.", ephemeral=True)

    @get.subcommand(name="elligibles", description="Get the number of servers eligible for random server command.")
    @scan_channel_only()
    async def elligibles(self, ctx):
        await ctx.response.defer()
        count = await self.craftprobe_db.num_union_servers()
        await ctx.followup.send(f"✅ There are {count} eligible servers for the random server command.")

    @craftprobe.subcommand(name="seen", description="Check if a player has been seen on the server.")
    @bot_channel_only()
    async def seen(self, ctx):
        pass

    @seen.subcommand(name="player", description="Check if player has been seen.")
    @bot_channel_only()
    async def player(self, ctx: nextcord.Interaction, username: str):
        await ctx.response.defer()
        timestamps = await self.craftprobe_db.when_was_player_seen(username)
        
        if timestamps is not None:
            timestamps_str = "\n".join([timestamp.strftime("%Y-%m-%d %H:%M:%S") for timestamp in timestamps])
            await ctx.followup.send(f"✅ Player {username} is in the database.\nTimes seen at (UTC):\n{timestamps_str}")
        else:
            await ctx.followup.send(f"❌ Player {username} is not in the database.")

    @seen.subcommand(name="server", description="Check if server has been seen.")
    @bot_channel_only()
    async def server(self, ctx: nextcord.Interaction, server_ip: str):
        await ctx.response.defer(ephemeral=True)
        try:
            server = server_ip.split(":")[0]
            port = server_ip.split(":")[1]
        except IndexError:
            await ctx.followup.send("Invalid server IP format. Please use the format `ip:port`.", ephemeral=True)
            return
        seen = await self.craftprobe_db.is_server_seen(server, port)
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
        await self.craftprobe_db.preprocess()
        await ctx.followup.send("✅ Database preprocessed.")

    @craftprobe.subcommand(name="number", description="Various counts from the database.")
    async def number(self, ctx):
        pass

    @craftprobe.subcommand(name="leaderboard", description="Various leaderboards from the database.")
    async def leaderboard(self, ctx):
        pass

    @number.subcommand(name="players", description="Get the number of unique players in the database.")
    async def number_players(self, ctx):
        await ctx.response.defer()
        count = await self.craftprobe_db.get_number_of_players()
        await ctx.followup.send(f"✅ There are {count} unique players in the database.")

    @number.subcommand(name="servers", description="Get the number of unique servers in the database.")
    async def number_servers(self, ctx):
        await ctx.response.defer()
        count = await self.craftprobe_db.get_number_of_servers()
        await ctx.followup.send(f"✅ There are {count} unique servers in the database.")

    @leaderboard.subcommand(name="players", description="Get the top 10 most seen players in the database.")
    async def leaderboard_players(self, ctx):
        await ctx.response.defer()
        leaderboard: list[Tuple[str, int]] = await self.craftprobe_db.get_players_with_most_entries_in_players_seen()
        # create embed
        embed = nextcord.Embed(title="Top 10 Most Seen Players", description="The top 10 most seen players in the database.", color=0x00ff00)
        for i, (player_name, count) in enumerate(leaderboard):
            embed.add_field(name=f"{i+1}. {player_name}", value=f"Seen {count} times", inline=False)
        await ctx.followup.send(embed=embed)

    @get.subcommand(name="hosting_ips", description="Get likely server hosting provider IPs.")
    async def hosting_ips(self, ctx):
        await ctx.response.defer()
        hosting_ips: list[Tuple[str, int]] = await self.craftprobe_db.get_likely_server_hosting_ips()
        if hosting_ips:
            response = "✅ Likely server hosting provider IPs:\n\n"
            for ip, count in hosting_ips:
                response += f"{ip} - {count} different ports\n"
            await ctx.followup.send(response)
        else:
            await ctx.followup.send("❌ No likely server hosting provider IPs found.")
