import nextcord
from nextcord.ext import commands
import asyncio

class DemocracyCommands(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.active_votes = {}  # active votekicks
    
    @nextcord.slash_command(name="votekick", description="Votekick user.")
    @commands.has_permissions(send_messages=True)
    async def votekick(self, ctx, member: nextcord.Member):
        """Start a votekick against a member."""
        
        if member == ctx.author:
            pass
            # Commented because funny
            # await ctx.send("❌ You cannot votekick yourself!")
            # return
        
        if member == ctx.guild.owner:
            await ctx.send("❌ You cannot votekick Great Leader Poplatvia!")
            return
        
        if member.bot:
            await ctx.send("❌ You cannot votekick a bot!")
            return
        
        # Check if there's already an active votekick for this member
        if member.id in self.active_votes:
            await ctx.send(f"❌ There's already an active votekick against {member.mention}!")
            return
        
        await self.db.add_votekick(member.id, ctx.author.id)
        
        # Create the votekick message
        embed = nextcord.Embed(
            title="🗳️ VOTEKICK IN PROGRESS",
            description=f"**Votekick against:** {member.mention}\n\n**Requirement:** 5 reactions to kick",
            color=nextcord.Color.red()
        )
        embed.add_field(name="Started by", value=ctx.author.mention, inline=False)
        embed.add_field(name="React with 👍 to vote for the kick", value="Current reactions: 0/5", inline=False)
        
        votekick_message = await ctx.send(embed=embed)
        
        await votekick_message.add_reaction("👍")
        
        # structure of active votekick and store it
        self.active_votes[member.id] = {
            "message_id": votekick_message.id,
            "member": member,
            "guild_id": ctx.guild.id,
            "started_by": ctx.author
        }
        
        TIMEOUT = 5*60
        
        await asyncio.sleep(TIMEOUT)
        
        # Check if the votekick is still active
        if member.id not in self.active_votes:
            return
        
        # fetch message then check reactions
        try:
            votekick_msg = await ctx.channel.fetch_message(votekick_message.id)
            
            reaction_count = 0
            for reaction in votekick_msg.reactions:
                if reaction.emoji == "👍":
                    reaction_count = reaction.count - 1  # -1 to exclude bot's own reaction
                    break
     
            if reaction_count >= 5:
                try:
                    await member.kick(reason=f"Votekick initiated by {ctx.author} with {reaction_count} votes")
              
                    success_embed = nextcord.Embed(
                        title="✅ VOTEKICK SUCCESSFUL",
                        description=f"{member.mention} has been kicked with {reaction_count} votes!",
                        color=nextcord.Color.green()
                    )
                    await votekick_msg.edit(embed=success_embed)
                    
                except nextcord.Forbidden:
                    await ctx.send(f"❌ I don't have permission to kick {member.mention}!")
            else:
                # failed
                fail_embed = nextcord.Embed(
                    title="❌ VOTEKICK FAILED",
                    description=f"Not enough votes ({reaction_count}/5) to kick {member.mention}",
                    color=nextcord.Color.orange()
                )
                await votekick_msg.edit(embed=fail_embed)
            
            del self.active_votes[member.id]
            
        except nextcord.NotFound:
            # Message was deleted
            if member.id in self.active_votes:
                del self.active_votes[member.id]