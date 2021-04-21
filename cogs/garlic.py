import os
import requests
import random
import re
import config

from discord.ext import commands
from config import default

class Garlic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        config = default.config()
        # self.gify_api_key = config['gify']['api_key']
        # self.gify_api_url = config['gify']['api_url']
        self.gify_api_key = config.gify.api_key
        self.gify_api_url = config.gify.api_url

    @commands.command(
        name='greet',
        help='Greets the user using whatever argument passed.',
        )
    async def salute(self, ctx, arg):
        await ctx.send('{0}! {1}'.format(arg, ctx.author.mention))

    @commands.command(
        name = 'gif',
        aliases = ['g'],
        help='Send GIFs based on the search text passed.'
        )
    async def send_gif(self, ctx, arg):
        body = [
            ('api_key', self.gify_api_key),
            ('q', arg),
            ('limit', 50),
            ('lang', 'en')
        ]
        res = requests.get(self.gify_api_url, params=body)
        if res.status_code != 200:
            await ctx.send('Oops! Something went wrong. Please try again.')
        elif len(res.json()['data']) > 0:
            gif = res.json()['data'][random.randrange(0, len(res.json()['data']))]
            await ctx.send(gif['embed_url'])
        else:
            await ctx.send('No results found for keyword "{0}".'.format(arg))

    @commands.command(
        name='insult',
        help='You can insult by @mentioning someone. Good luck!'
    )
    async def insult_someone(self, ctx, arg):
        if re.compile(r'\d+').search(arg).group() == str(self.bot.user.id):
            await ctx.send(f'Hey! {ctx.author.mention}, You can\'t insult me.')
        else:
            try: 
                res = requests.get('https://evilinsult.com/generate_insult.php?lang=en&type=json')
                if res.status_code != 200:
                    raise Exception('Oops! Something went wrong.')
            except Exception as e:
                print(e)
                await ctx.send(f'{arg}, You\'re lucky.')
            else:
                await ctx.send(f'{arg} {res.json()["insult"]}')

def setup(bot):
    bot.add_cog(Garlic(bot))                  
        