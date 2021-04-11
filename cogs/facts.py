import discord
import requests

from discord.ext import commands

class Facts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name = 'doggo',
        aliases = ['dog', 'dogs'],
        help = 'Get random doogo facts'
    )
    async def doggo_facts(self, ctx):
        try:
            request_url = 'https://api.thedogapi.com/v1/images/search'
            res = requests.get(request_url)
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
                await ctx.send(f'__**{name}**__\n**Height:** {height}  **Weight:** {weight}\n{temperament}\n{gif}')
        except Exception as err:
            print(err)
            await ctx.send('Something went wrong, finding someone to blame...')   

def setup(bot):
    bot.add_cog(Facts(bot)) 