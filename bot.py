import asyncio
import discord
from discord.ext import commands
from config import COMMAND_PREFIX, DISCORD_TOKEN, GUILD_ID
from supabase_setup import supabase


class MealManBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default() #sets the intents of the bot to default
        intents.message_content = True 
        super().__init__(command_prefix=COMMAND_PREFIX, intents=intents) #inherits from the Bot class, and adds those two parameters.

    async def setup_hook(self):
        """Load commands and sync cogs on startup"""

        await self.load_extension('cogs.ping')
        await self.load_extension('cogs.register')
        await self.load_extension('cogs.recipe')
        await self.tree.sync(guild=discord.Object(id=GUILD_ID))
        await self.tree.sync()


async def main():
    bot = MealManBot()
    async with bot:
        await bot.start(DISCORD_TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
