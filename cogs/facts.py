import discord
import requests

from discord.ext import commands
from config import default


class Facts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        config = default.config()
        self.number_api_url, self.doggo_api_url = config.facts.number_api_url, config.facts.doggo_api_url

    @commands.command(
        name='randomnum',
        help='Gives random number facts.'
    )
    async def number_trivia(self, ctx):
        res = requests.get(self.number_api_url)
        if res.status_code != 200:
            await ctx.send('Oops! Something went wrong. Please try again.')
        else:
            await ctx.send(res.text)    

    @commands.command(
        name = 'doggo',
        aliases = ['dog', 'dogs'],
        help = 'Get random doggo facts'
    )
    async def doggo_facts(self, ctx):
        try:
            res = requests.get(self.doggo_api_url)
            doggo_details = res.json()[0]
            gif = doggo_details['url']
            # If no breed details, return just the gif
            if not len(doggo_details['breeds']):
                await ctx.send(gif)
            else:
                breed_details = doggo_details['breeds'][0]
                name = breed_details['name']
                temperament = breed_details['temperament']
                height = breed_details['height']['metric'] + ' cm'
                weight = breed_details['weight']['metric'] + ' kg'
                life_span = breed_details['life_span']
                await ctx.send(f'__**{name}**__\n**Height:** {height}  **Weight:** {weight}  **Life Span:** {life_span}\n{temperament}')
                await ctx.send(gif)
        except Exception as err:
            print(err)
            await ctx.send('Something went wrong, finding someone to blame...')   

def setup(bot):
    bot.add_cog(Facts(bot)) 