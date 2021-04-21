import discord
import requests

from discord.ext import commands
from config import default


class Jokes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        config = default.config()
        self.cn, self.dadjoke = config.jokes.norris, config.jokes.dadjoke

    @commands.command(
        name = 'dadjoke',
        aliases = ['dadjokes'],
        help = 'Hits you with a dad joke!'
    )
    async def dad_jokes(self, ctx):
        try:
            requestUrl = self.dadjoke
            headers = {'Accept': 'application/json'}
            joke = requests.get(requestUrl, headers=headers)
            joke = joke.json()['joke']
            await ctx.send(f'{joke}')
        except Exception as err:
            print(err)
            await ctx.send('Something went wrong...') 

    @commands.command(
        name='cn',
        help='Retrieve a random chuck joke.'
    )
    async def chuck_norris(self, ctx):
        res = requests.get(self.cn)
        if res.status_code != 200:
            await ctx.send('Oops! Something went wrong. Please try again.')
        else:
            data = res.json()
            for i in ['icon_url', 'value']:
                await ctx.send(data[i])               

def setup(bot):
    bot.add_cog(Jokes(bot))         