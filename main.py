import os
import config

from dotenv import load_dotenv
from discord.ext import commands
from config import default

# load_dotenv()
print('Loading config...')
config = default.config()


print("Initializing...")
bot = commands.Bot(command_prefix= config.bot_prefix, help_command=None)

'''
Token (Prod): ODEzMDYwMjIyMDQ1NjUxMDE0.YDJzVg.3AN8EzCEa4r9nCVomh2lqHGy0Ho
Token (Dev): ODMwNDYwNTAzNjUzODc1NzEy.YHHAnQ.a7ciLlu-WDs8noEnYYhkwVVoKWQ

Link to add bot to server (Prod): https://discord.com/api/oauth2/authorize?client_id=813060222045651014&permissions=518208&scope=bot

Link to add bot to server (Dev): https://discord.com/api/oauth2/authorize?client_id=830460503653875712&permissions=519232&scope=bot
'''

# Load cogs
with os.scandir('cogs') as dir:
    for entry in dir:
        if entry.is_file():
            bot.load_extension(f"cogs.{entry.name[:-3]}")

# Trigger the bot.
try: 
    # bot.run(config['bot_token'])
    bot.run(config.bot_token)
except Exception as e:
    print(f'Login error: {e}')    
