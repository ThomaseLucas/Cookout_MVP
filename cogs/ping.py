import discord 
from discord import app_commands
from discord.ext import commands
from utils.logger import logger

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='ping', description='Check the bot''s latency')
    @app_commands.default_permissions(administrator=True)
    async def ping(self, interaction: discord.Interaction):
        logger.info(f'Ping command received from {interaction.user.name}')
        
        #get the bot's latency
        latency = round(self.bot.latency * 1000)

        await interaction.response.send_message(
            f'Pong! \nlatency: {latency}ms',
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Ping(bot))
    logger.info('Ping cog loaded')

