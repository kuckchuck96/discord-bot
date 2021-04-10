import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import requests
import random


load_dotenv()

bot = commands.Bot(command_prefix='>')

'''
Token (Prod): ODEzMDYwMjIyMDQ1NjUxMDE0.YDJzVg.3AN8EzCEa4r9nCVomh2lqHGy0Ho
Token (Dev): ODMwNDYwNTAzNjUzODc1NzEy.YHHAnQ.a7ciLlu-WDs8noEnYYhkwVVoKWQ

Link to add bot to server (Prod): https://discord.com/api/oauth2/authorize?client_id=813060222045651014&permissions=518208&scope=bot

Link to add bot to server (Dev): https://discord.com/api/oauth2/authorize?client_id=830460503653875712&permissions=519232&scope=bot
'''

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name='lasangiri'))

    if bot.user.avatar == None:
        image_path = 'images/garlic_icon.png'
        with open(image_path, 'rb') as f:
            image = f.read()
        
        await bot.user.edit(avatar=image)
    
    print(bot.user.name + ' is online.')

@bot.command(
    name='s',
    help='Greets the user using whatever argument passed.',
    )
async def salute(ctx, arg):
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
    elif len(res.json()['data']) > 0:
        gif = res.json()['data'][random.randrange(0, len(res.json()['data']))]
        await ctx.send(gif['embed_url'])
    else:
        await ctx.send('No results found for keyword "{0}".'.format(arg))

@bot.command(
    name='num',
    help='Gives random number facts.'
)
async def number_trivia(ctx):
    res = requests.get('http://numbersapi.com/random/trivia')
    if res.status_code != 200:
        await ctx.send('Oops! Something went wrong. Please try again.')
    else:
        await ctx.send(res.text)

@bot.command(
    name='cn',
    help='Retrieve a random chuck joke.'
)
async def chuck_norris(ctx):
    res = requests.get('https://api.chucknorris.io/jokes/random')
    if res.status_code != 200:
        await ctx.send('Oops! Something went wrong. Please try again.')
    else:
        data = res.json()
        for i in ['icon_url', 'value']:
            await ctx.send(data[i])

# Trigger the bot.
bot.run(os.getenv('BOT_TOKEN'))
