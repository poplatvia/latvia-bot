import nextcord
from nextcord.ext.application_checks import check
from Config import Config

conf = Config()

def bot_channel_only():
    async def predicate(interaction: nextcord.Interaction):
        if interaction.channel_id not in conf.config["bot_channels"]:
            await interaction.response.send_message("❌ You can only use bot commands in the bot channel.", ephemeral=True)
            return False
        return True
    return check(predicate)