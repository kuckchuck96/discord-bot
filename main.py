import discord
import os
from dotenv import load_dotenv

load_dotenv()
client = discord.Client()


# Token: ODEzMDYwMjIyMDQ1NjUxMDE0.YDJzVg.3AN8EzCEa4r9nCVomh2lqHGy0Ho

# Link to add bot to server: https://discord.com/api/oauth2/authorize?client_id=813060222045651014&permissions=518208&scope=bot

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.idle, activity=discord.Game('Listening to lasangiri'))
    print('I\'m online.')

@client.event
async def on_message(msg):
    data = msg.content.lower()

    if msg.author == client.user:
        return
    
    if data.startswith(('hello', 'hi', 'yo')):
        await msg.channel.send('Yo! {0}'.format(msg.author))

client.run(os.getenv('BOT_TOKEN'))
