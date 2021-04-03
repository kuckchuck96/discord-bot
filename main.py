import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import requests
import random


load_dotenv()
#client = discord.Client()

bot = commands.Bot(command_prefix='>')

# Token: ODEzMDYwMjIyMDQ1NjUxMDE0.YDJzVg.3AN8EzCEa4r9nCVomh2lqHGy0Ho

# Link to add bot to server: https://discord.com/api/oauth2/authorize?client_id=813060222045651014&permissions=518208&scope=bot

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('Listening to lasangiri'))
    print(bot.user.name + ' is online.')

@bot.command(
    name='s',
    help='Greets the user using whatever argument passed.',
    )
async def salute(ctx, arg):
    # print(ctx.author)
    await ctx.send('{0}! {1}'.format(arg, ctx.author.mention))

@bot.command(
    name='g',
    help='Send GIFs based on the search text passed.'
    )
async def send_gif(ctx, arg):
    body = [
        ('api_key', os.getenv('GIFY_API_KEY')),
        ('q', arg),
        ('limit', 25),
        ('lang', 'en'),
        ('rating', 'pg-13')
    ]
    res = requests.get(os.getenv('GIFY_API_URL'), params=body)
    if res.status_code != 200:
        await ctx.send('Oops! Something went wrong. Please try again.')
    if len(res.json()['data']) > 0:
        gif = res.json()['data'][random.randrange(0, len(res.json()['data']))]
        await ctx.send(gif['embed_url'])
    else:
        await ctx.send('No results found for keyword "{0}".'.format(arg))

# @bot.event
# async def on_message(msg):
#     if bot.user == msg.author:
#         return 
#     # print(msg.author)
#     # print(msg.content)
#     await bot.process_commands(msg)

# @bot.event
# async def on_message(msg):
#     await msg.channel.send('Yo! {0}'.format(msg.author))

# @client.event
# async def on_message(msg):
#     await msg.channel.send('Yo! {0}'.format(msg.author))
        
bot.run(os.getenv('BOT_TOKEN'))
# client.run(os.getenv('BOT_TOKEN'))