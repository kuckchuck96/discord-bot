import discord
import os
import requests
import random

from dotenv import load_dotenv
from discord.ext import commands


load_dotenv()
print("Initializing...")
bot = commands.Bot(command_prefix='>')

# Token: ODEzMDYwMjIyMDQ1NjUxMDE0.YDJzVg.3AN8EzCEa4r9nCVomh2lqHGy0Ho

# Link to add bot to server: https://discord.com/api/oauth2/authorize?client_id=813060222045651014&permissions=518208&scope=bot

for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")

# Trigger the bot.
try: 
    bot.run(os.getenv('BOT_TOKEN'))
except Exception as e:
    print(f'Login error: {e}')    
