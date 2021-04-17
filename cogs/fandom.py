import discord
from discord import embeds
from discord.ext import commands
import hashlib
import os
import requests
from types import SimpleNamespace
import json
from datetime import datetime as dt


class Fandom(commands.Cog):
    
    def __init__(self, bot) -> None:
        self.bot = bot
        self.marv_env_list = ['MARV_TS', 'MARV_PRIVATE_KEY', 'MARV_PUBLIC_KEY']

    @commands.command(
        name='marvel',
        help='Search for your favourite Marvel character.'
    )
    async def get_marvel_character(self, ctx, *arg) -> None: 
        char_name = '-'.join(list(map(lambda c: c.capitalize(), arg[0].split('-')))) if len(arg) == 1 and str(arg[0]).count('-') else ' '.join(list(map(lambda c: c.capitalize(), arg)))  

        body = [
            ('ts', os.getenv('MARV_TS')),
            ('apikey', os.getenv('MARV_PUBLIC_KEY')),
            ('hash', self.create_hash()),
            ('name', char_name)
        ]

        try:
            res = requests.get(os.getenv('MARV_CHARACTERS_URL'), params=body)
            if res.status_code != 200:
                raise Exception('Oops! Something went wrong.')
        except Exception as ex:
            print(ex)
            await ctx.send(ex)
        else:   
            # Convert json response to object.
            obj = json.loads(res.text, object_hook=lambda o: SimpleNamespace(**o))

            if len(obj.data.results) > 0:
                # Fetch most used attribute.
                results = obj.data.results[0]

                card = discord.Embed(
                    title=results.name,
                    description=results.description,
                    color = discord.Color.red(),
                    timestamp=dt.strptime(results.modified.split('T')[0], '%Y-%m-%d')
                )
                card.set_footer(text=f'* {obj.attributionText}')
                thumbnail = results.thumbnail
                card.set_thumbnail(url=f'{thumbnail.path}/portrait_medium.{thumbnail.extension}')
                for f in ['comics', 'series', 'stories', 'events']:
                    card.add_field(name=f.capitalize(), value=eval(f'results.{f}.available'))
                await ctx.send(embed=card)
            else:
                await ctx.send(f'Cannot fetch dets for **{char_name}**.')
            
    def create_hash (self):
        hash = hashlib.md5()
        for k in self.marv_env_list:
            hash.update(os.getenv(k).encode('utf-8'))
        return hash.hexdigest()

def setup(bot):
    bot.add_cog(Fandom(bot)) 