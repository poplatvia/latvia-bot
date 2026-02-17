import nextcord
from nextcord.ext import commands
import asyncio
from datetime import datetime, timedelta

class DemocracyCommands(commands.Cog):
    def __init__(self, bot, db, admins: list[int]):
        self.bot = bot
        self.db = db
        self.active_votes = {}  # active votekicks
        self.admins = admins
    
    @nextcord.slash_command(name="votekick", description="Votekick user.")
    @commands.has_permissions(send_messages=True)
    async def votekick(self, ctx, member: nextcord.Member):
        """Start a votekick against a member."""
        
        if member == ctx.user.id:
            pass
            # Commented because funny
            # await ctx.send("❌ You cannot votekick yourself!")
            # return

        time_since_first_message = await self.db.time_since_first_message(member.id)
        if time_since_first_message < timedelta(days=1):
            await ctx.send(f"⚠️ {member.mention}, you need to have been active for at least a day to participate in votekicks.", delete_after=5)
            return

        if member.id in self.admins:
            await ctx.send("❌ You cannot votekick Great Leader Poplatvia!")
            return
        
        if member.bot:
            await ctx.send("❌ You cannot votekick a bot!")
            return
    
        
        # Check if there's already an active votekick for this member
        if member.id in self.active_votes:
            await ctx.send(f"❌ There's already an active votekick against {member.mention}!")
            return
        
        await self.db.add_votekick(member.id, ctx.user.id)

        defendants_elo = await self.db.calculate_elo(member.id)
        # If user has perfect elo, number of votes needed is 20.
        num_votes_needed = max(3, int(defendants_elo/5))
        
        # Create the votekick message
        embed = nextcord.Embed(
            title="🗳️ VOTEKICK IN PROGRESS",
            description=f"**Votekick against:** {member.mention}\n\n**Requirement:** {num_votes_needed} reactions to kick",
            color=nextcord.Color.red()
        )
        embed.add_field(name="Started by", value=ctx.user.mention, inline=False)
        embed.add_field(name=f"React with 👍 to vote for the kick", value=f"Current reactions: 0/{num_votes_needed}", inline=False)
        
        await ctx.send(f"Votekick started against {member.mention}!", ephemeral=True)
        votekick_message = await ctx.channel.send(embed=embed)
        await votekick_message.add_reaction("👍")

        # structure of active votekick and store it
        self.active_votes[member.id] = {
            "message_id": votekick_message.id,
            "channel_id": ctx.channel.id,
            "member": member,
            "guild_id": ctx.guild.id,
            "started_by": ctx.user,
            "required_votes": num_votes_needed,
            "expires_at": datetime.utcnow() + timedelta(minutes=5)
        }
        
        self.bot.loop.create_task(self._votekick_timeout(member.id, ctx.channel, votekick_message.id))
    
    async def _votekick_timeout(self, member_id: int, channel, message_id: int):
        """Handle votekick timeout after 5 minutes."""
        await asyncio.sleep(5 * 60)
        
        if member_id not in self.active_votes:
            return
        
        try:
            votekick_msg = await channel.fetch_message(message_id)
            
            reaction_count = 0
            for reaction in votekick_msg.reactions:
                if reaction.emoji == "👍":
                    reaction_count = reaction.count - 1
                    break
            
            # votekick failed
            fail_embed = nextcord.Embed(
                title="❌ VOTEKICK FAILED",
                description=f"Votekick started by {self.active_votes[member_id]['started_by'].mention} against {self.active_votes[member_id]['member'].mention} failed. Time expired with {reaction_count}/{self.active_votes[member_id]['required_votes']} votes",
                color=nextcord.Color.orange()
            )
            await votekick_msg.edit(embed=fail_embed)
            
            del self.active_votes[member_id]
            
        except (nextcord.NotFound, KeyError):
            if member_id in self.active_votes:
                del self.active_votes[member_id]
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Monitor reactions on votekick messages."""
        if user.bot:
            return
        
        for member_id, vote_data in list(self.active_votes.items()):
            if reaction.message.id == vote_data["message_id"] and reaction.emoji == "👍":
                reaction_count = reaction.count - 1
                
                embed = reaction.message.embeds[0]
                embed.set_field_at(
                    1, 
                    name="React with 👍 to vote for the kick",
                    value=f"Current reactions: {reaction_count}/{vote_data['required_votes']}",
                    inline=False
                )
                await reaction.message.edit(embed=embed)
                
                # Check if threshold is reached
                if reaction_count >= vote_data['required_votes']:
                    member = vote_data["member"]
                    started_by = vote_data["started_by"]
                    
                    try:
                        await member.kick(reason=f"Votekick initiated by {started_by} with {reaction_count} votes")
                        
                        success_embed = nextcord.Embed(
                            title="✅ VOTEKICK SUCCESSFUL",
                            description=f"{member.mention} has been kicked with {reaction_count} votes!",
                            color=nextcord.Color.green()
                        )
                        await reaction.message.edit(embed=success_embed)
                        
                    except nextcord.Forbidden:
                        error_embed = nextcord.Embed(
                            title="❌ VOTEKICK ERROR",
                            description=f"I don't have permission to kick {member.mention}!",
                            color=nextcord.Color.red()
                        )
                        await reaction.message.edit(embed=error_embed)
                    
                    # Remove from active votes
                    del self.active_votes[member_id]
                
                break