import discord
from discord import embeds
from discord.ext import commands
import hashlib
import os
import requests


class Fandom(commands.Cog):
    
    def __init__(self, bot) -> None:
        self.bot = bot
        self.marv_env_list = ['MARV_TS', 'MARV_PRIVATE_KEY', 'MARV_PUBLIC_KEY']

    @commands.command(
        name='marvel'
    )
    async def get_all_marvel_characters(self, ctx, arg) -> None:
        # await ctx.send(self.create_hash())
        body = [
            ('ts', os.getenv('MARV_TS')),
            ('apikey', os.getenv('MARV_PUBLIC_KEY')),
            ('hash', self.create_hash()),
            ('name', arg)
        ]

        try:
            res = requests.get(os.getenv('MARV_CHARACTERS_URL'), params=body)
            if res.status_code != 200:
                raise Exception('Oops! Something went wrong.')
        except Exception as ex:
            print(ex)
            await ctx.send(ex)
        else:   
            results = res.json()['data']['results'][0]
            card = discord.Embed(
                title=results['name'],
                description=results['description'],
                color = discord.Color.red()
            )
            card.set_footer(text=res.json()['attributionText'])
            for f in ['comics', 'series', 'stories', 'events']:
                card.add_field(name=f.capitalize(), value=results[f]['available'])
            await ctx.send(embed=card)
            

    def create_hash (self):
        hash = hashlib.md5()
        for k in self.marv_env_list:
            hash.update(os.getenv(k).encode('utf-8'))
        return hash.hexdigest()

def setup(bot):
    bot.add_cog(Fandom(bot)) 