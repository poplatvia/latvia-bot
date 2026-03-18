import nextcord
from nextcord.ext import commands
from db.CraftprobeDb import CraftprobeDb
from datetime import datetime

class Bullshit(commands.Cog):
    def __init__(self, context):
        self.bot = context.client
        self.db = context.db
        self.config = context.config

    @nextcord.slash_command(name="quote", description="Get a random quote from the database.")
    async def quote(self, ctx):
        await ctx.response.defer()
        user_id, quote, date = await self.db.get_random_quote()
        date: datetime = datetime.fromisoformat(date) if date else None
        # extract only date
        date = date.date() if date else None
        if quote and user_id:
            await ctx.response.send_message(f'"{quote}" - <@{user_id}> on {date}')
        else:
            await ctx.response.send_message("No quotes available.")

    @nextcord.slash_command(name="rage", description="Get a random angry message from the database.")
    async def rage(self, ctx):
        await ctx.response.defer()
        user_id, message, date = await self.db.get_random_message_with_curses(min_curses=3)
        date: datetime = datetime.fromisoformat(date) if date else None
        date = date.date() if date else None
        if message and user_id:
            await ctx.response.send_message(f'😤 {message}\n— <@{user_id}> on {date}')
        else:
            await ctx.response.send_message("No rage available.")
