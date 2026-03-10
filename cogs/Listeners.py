import asyncio

import nextcord
from nextcord.ext import commands
from db.Db import Db
import random

class Listeners(commands.Cog):
    def __init__(self, bot, db, language, ai, config):
        self.bot = bot
        self.db: Db = db
        self.language = language
        self.ai = ai
        self.config = config

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: nextcord.Reaction, user: nextcord.Member):
        if user.bot:
            return
        await self.db.add_reaction(reaction.message.id, user.id, reaction.emoji, "add")
            
        print(f"{user.name} reacted with {reaction.emoji} on message {reaction.message.id}")

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction: nextcord.Reaction, user: nextcord.Member):
        if user.bot:
            return
        await self.db.add_reaction(reaction.message.id, user.id, reaction.emoji, "remove")
        print(f"{user.name} removed reaction {reaction.emoji} from message {reaction.message.id}")

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author.bot:
            return

        await self.db.add_message(message.id, message.author.id, message.channel.id, message.content)

        if self.language.contains_really_bad_language(message.content):
            await message.delete()
            await message.channel.send(f"⚠️ {message.author.mention}, your message contained inappropriate language and has been removed.", delete_after=5)
        elif self.language.contains_curse_words(message.content):
            await message.channel.send(f"⚠️ {message.author.mention}, watch your language!", delete_after=5)
        
        is_english = self.language.is_english(message.content)
        print(f"Processed {'English' if is_english else 'Non-English'} message from {message.author}: {message.content}")

        if random.random() < 0.2 and "?" in message.content:        
            loop = asyncio.get_event_loop()
            all_messages = await self.db.get_all_messages()
            all_messages = random.sample(all_messages, min(500, len(all_messages)))

            async with message.channel.typing():
                r = await loop.run_in_executor(
                    None, 
                    self.ai.reply_with_replicated_speech, 
                    message.content, 
                    all_messages
                )

            print("Finished AI response.")

            await message.channel.send(f"{r}")

    async def cog_unload(self):
        await self.db.close()
