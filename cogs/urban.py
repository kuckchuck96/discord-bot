import discord
import os
import requests

from discord.ext import commands

class UrbanDictionary(commands.Cog):
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
            print(res)
            if res.status_code != 200:
                await ctx.send('Oops! Something went wrong. Please try again.')
            # Convert to json    
            res = res.json()
            # Handle no matches
            if not len(res['list']):
                return await ctx.send("What alien language is that!! No matches...")
            # Sort by votes and pick the highest
            res = sorted(res['list'], reverse=True, key=lambda g: int(g["thumbs_up"]))[0]
            definition = res['definition']
            await ctx.send(f"📖 Urban Dictionary definition for **{res['word']}**```\n{definition}```")    
        except Exception:
            await ctx.send('Urban Dictionary API must be down.')

def setup(bot):
    bot.add_cog(UrbanDictionary(bot))      