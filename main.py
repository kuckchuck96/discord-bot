import discord
import os

from discord.ext.commands import bot
import config
import sys

# from dotenv import load_dotenv
from discord.ext import commands
from config import default

# Set file path to access util classes in cogs
sys.path.append("./utils/")

# Commented for heroku deployment
# load_dotenv()
print('Loading config...')
config = default.config()

print("Initializing...")
# bot = commands.Bot(command_prefix= config.bot_prefix, help_command=None)

bot_options = {
    'command_prefix': config.bot_prefix,
    'help_command': None
}

# Enable bot with intents support
if config.enable_all_intents and os.getenv('INTENTS_SUPPORTED') == 'true':
    intents = discord.Intents.all()
    print('Intents enabled.')
    # bot = commands.Bot(command_prefix= config.bot_prefix, help_command=None, intents=intents)
    bot_options['intents'] = intents

bot = commands.Bot(**bot_options)

# Load cogs
with os.scandir('cogs') as dir:
    for entry in dir:
        if entry.is_file():
            bot.load_extension(f"cogs.{entry.name[:-3]}")

# Trigger the bot.
try: 
    bot.run(config.bot_token)
except Exception as e:
    print(f'Login error: {e}')    
