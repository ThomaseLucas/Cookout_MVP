import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
COMMAND_PREFIX = '!'
GUILD_ID = '1371890720734056448'