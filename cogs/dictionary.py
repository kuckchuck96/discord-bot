import discord
import requests
import random
import config

from discord.ext import commands
from config import default


class Dictionary(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        config = default.config()
        self.urban_dictionary_api_url = config.urban_dictionary.api_url

    @commands.command(
        name = 'define',
        help = 'Fetch definition from Urban Dictionary'
    )
    async def urban_define(self, ctx, *args):
        try:
            args = ' '.join(args)
            if not len(args):
                return await ctx.send('Define what?')
            request_url = f'{self.urban_dictionary_api_url}/define?term={args}'
            res = requests.get(request_url)
            if res.status_code != 200:
                return await ctx.send('Oops! Something went wrong. Please try again.')
            # Convert to json    
            res = res.json()
            # Handle no matches
            if not len(res['list']):
                return await ctx.send("What alien language is that!! No matches...")
            # Get random definitions - changed from highest vote to random
            res = res['list'][random.randrange(0, len(res['list']))]
            definition = res['definition'].replace('[', '').replace(']', '')
            await ctx.send(f"📖 Urban Dictionary definition for **{res['word']}**```\n{definition}```")    
        except Exception:
            await ctx.send('Urban Dictionary API must be down.')

    @commands.command(
        name = 'randomword',
        aliases = ['urban', 'word'],
        help = 'Fetches random word from Urban Dictionary'
    )
    async def random(self, ctx): 
        try:
            request_url = f'{self.urban_dictionary_api_url}/random'
            res = requests.get(request_url)
            res = res.json()['list'][random.randrange(0, len(res.json()['list']))]
            word = res['word'].replace('[', '').replace(']', '')
            definition = res['definition'].replace('[', '').replace(']', '')
            await ctx.send(f'Random word from Urban Dictionary: \n**Word:** {word}\n**Definition:** {definition}')
        except Exception:
            await ctx.send('Urban Dictionary API must be down.')         

def setup(bot):
    bot.add_cog(Dictionary(bot))      