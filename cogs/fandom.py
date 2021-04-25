import discord
from discord.ext import commands
import hashlib
import requests
from types import SimpleNamespace
import json
from datetime import datetime as dt
from config import default


class Fandom(commands.Cog):
    
    def __init__(self, bot) -> None:
        self.bot = bot
        self.conf = default.config()

    def call_api(self, url, params) -> str:
        res = requests.get(url=url, params=params)
        if res.status_code != 200:
            return None
        return res.text

    # Pass JSON as string.
    def json_to_obj_parser(self, data):
        return json.loads(data, object_hook=lambda o: SimpleNamespace(**o)) if data != None else None
  

    @commands.command(
        name='marvel',
        help='Search for your favourite Marvel character.'
    )
    async def get_marvel_character(self, ctx, *arg) -> None: 
        char_name = '-'.join(list(map(lambda c: c.capitalize(), arg[0].split('-')))) if len(arg) == 1 and str(arg[0]).count('-') else ' '.join(list(map(lambda c: c.capitalize(), arg)))  

        body = [
            ('ts', self.conf.disney.ts),
            ('apikey', self.conf.disney.public_key),
            ('hash', self.create_hash()),
            ('name', char_name)
        ]

        try:
            res = requests.get(self.conf.disney.marvel_api_url, params=body)
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
        hash.update(str(self.conf.disney.ts).encode('utf-8'))
        hash.update(str(self.conf.disney.private_key).encode('utf-8'))
        hash.update(str(self.conf.disney.public_key).encode('utf-8'))
        return hash.hexdigest()

    @commands.command(
        name='sw',
        help='Search your favourite Star Wars character.'
    )
    async def star_wars_data(self, ctx, *arg):
        name = ' '.join(arg)
        try:
            res = requests.get(self.conf.disney.sw_api_url, params=[('search', name)])
            if res.status_code != 200:
                raise Exception('Oops! Something went wrong.')

            # Convert json response to object.
            obj = self.json_to_obj_parser(res.text)
        
            if len(obj.results) > 0:
                results = obj.results[0]

                homeworld = self.call_api(results.homeworld, None)
                if homeworld != None:
                    homeworld_obj = self.json_to_obj_parser(homeworld)

                embed = discord.Embed(
                    title=f'{results.name} ({results.birth_year})',
                    description='From **'+ homeworld_obj.name +'**.' if homeworld_obj != None and str(homeworld_obj.name).strip().lower() != 'unknown' else '',
                    color = discord.Color.gold()
                )

                # Movies.
                if len(results.films) > 0:
                    value = []
                    for i, film in enumerate(results.films):
                        film_data = self.json_to_obj_parser(self.call_api(film, None))
                        if film_data != None:
                            value.append(f'{i+1}. {film_data.title} (Ep-{film_data.episode_id}, {film_data.release_date}).')
                    embed.add_field(name='Movie/s', value='\n'.join(value))

                # Starships.
                if len(results.starships):
                    value = []
                    for i, sf in enumerate(results.starships):
                        sf_data = self.json_to_obj_parser(self.call_api(sf, None))
                        if sf_data != None:
                            value.append(f'{i+1}. **{sf_data.model}** manufactured by **{sf_data.manufacturer}**.')
                    embed.add_field(name='Starship/s', value='\n'.join(value))
            else:
                raise Exception(f'No data found for **{name.capitalize()}**')
        except Exception as ex:
            await ctx.send(ex)
        else:
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Fandom(bot)) 