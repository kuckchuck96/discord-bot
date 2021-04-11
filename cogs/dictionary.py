import discord
import os
import requests
import random

from discord.ext import commands

class Dictionary(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name = 'define',
        help = 'Fetch definition from Urban Dictionary'
    )
    async def urban_define(self, ctx, *args):
        try:
            args = ' '.join(args)
            requestUrl = os.getenv('URBAN_API_URL') + '/define?term=' + args
            res = requests.get(requestUrl)
            if res.status_code != 200:
                await ctx.send('Oops! Something went wrong. Please try again.')
            # Convert to json    
            res = res.json()
            # Handle no matches
            if not len(res['list']):
                return await ctx.send("What alien language is that!! No matches...")
            # Sort by votes and pick the highest
            res = sorted(res['list'], reverse=True, key=lambda g: int(g["thumbs_up"]))[0]
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
            requestUrl = os.getenv('URBAN_API_URL') + '/random'
            res = requests.get(requestUrl)
            res = res.json()['list'][random.randrange(0, len(res.json()['list']))]
            word = res['word'].replace('[', '').replace(']', '')
            definition = res['definition'].replace('[', '').replace(']', '')
            await ctx.send(f'Random word from Urban Dictionary: \n**Word:** {word}\n**Definition:** {definition}')
        except Exception:
            await ctx.send('Urban Dictionary API must be down.')         

def setup(bot):
    bot.add_cog(Dictionary(bot))      