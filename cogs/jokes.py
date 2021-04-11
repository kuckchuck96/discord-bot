import discord
import requests

from discord.ext import commands

class Jokes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name = 'dadjoke',
        aliases = ['dadjokes'],
        help = 'Hits you with a dad joke!'
    )
    async def dad_jokes(self, ctx):
        try:
            requestUrl = 'https://icanhazdadjoke.com'
            headers = {'Accept': 'application/json'}
            joke = requests.get(requestUrl, headers=headers)
            joke = joke.json()['joke']
            await ctx.send(f'{joke}')
        except Exception as err:
            print(err)
            await ctx.send('Something went wrong...')        

def setup(bot):
    bot.add_cog(Jokes(bot))         