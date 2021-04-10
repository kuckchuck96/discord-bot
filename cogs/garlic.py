import discord
import os
import requests
import random

from discord.ext import commands

class Garlic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='s',
        help='Greets the user using whatever argument passed.',
        )
    async def salute(self, ctx, arg):
        await ctx.send('{0}! {1}'.format(arg, ctx.author.mention))

    @commands.command(
        name='g',
        help='Send GIFs based on the search text passed.'
        )
    async def send_gif(self, ctx, arg):
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

    @commands.command(
        name='num',
        help='Gives random number facts.'
    )
    async def number_trivia(self, ctx):
        res = requests.get('http://numbersapi.com/random/trivia')
        if res.status_code != 200:
            await ctx.send('Oops! Something went wrong. Please try again.')
        else:
            await ctx.send(res.text)

    @commands.command(
        name='cn',
        help='Retrieve a random chuck joke.'
    )
    async def chuck_norris(self, ctx):
        res = requests.get('https://api.chucknorris.io/jokes/random')
        if res.status_code != 200:
            await ctx.send('Oops! Something went wrong. Please try again.')
        else:
            data = res.json()
            for i in ['icon_url', 'value']:
                await ctx.send(data[i])

def setup(bot):
    bot.add_cog(Garlic(bot))                  
        