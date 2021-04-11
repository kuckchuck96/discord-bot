import discord
import os
import requests
import random

from dotenv import load_dotenv
from discord.ext import commands


# load_dotenv()


print("Initializing...")
bot = commands.Bot(command_prefix='>')

'''
Token (Prod): ODEzMDYwMjIyMDQ1NjUxMDE0.YDJzVg.3AN8EzCEa4r9nCVomh2lqHGy0Ho
Token (Dev): ODMwNDYwNTAzNjUzODc1NzEy.YHHAnQ.a7ciLlu-WDs8noEnYYhkwVVoKWQ

Link to add bot to server (Prod): https://discord.com/api/oauth2/authorize?client_id=813060222045651014&permissions=518208&scope=bot

Link to add bot to server (Dev): https://discord.com/api/oauth2/authorize?client_id=830460503653875712&permissions=519232&scope=bot
'''

with os.scandir('cogs') as dir:
    for entry in dir:
        if entry.is_file():
            bot.load_extension(f"cogs.{entry.name[:-3]}")

# for file in os.listdir("cogs"):
#     if file.endswith(".py"):
#         name = file[:-3]
#         bot.load_extension(f"cogs.{name}")

# Trigger the bot.
try: 
    bot.run(os.getenv('BOT_TOKEN'))
except Exception as e:
    print(f'Login error: {e}')    
