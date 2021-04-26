import json
import requests
import random
import re
import discord
from types import SimpleNamespace

from discord.ext import commands
from config import default


class Garlic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        config = default.config()
        self.tenor_api_key = config.tenor.api_key
        self.tenor_api_url = config.tenor.api_url

    @commands.command(
        name='greet',
        help='Greets the user using whatever argument passed.',
        )
    async def salute(self, ctx, arg):
        await ctx.send('{0}! {1}'.format(arg, ctx.author.mention))

    @commands.command(
        name = 'gif',
        aliases = ['g'],
        help='Send GIFs based on the search text passed.'
        )
    async def send_gif(self, ctx, *arg):
        params = [
            ('key', self.tenor_api_key),
            ('q', ' '.join(arg)),
            ('limit', 50),
            ('anon_id', ctx.author.id)
        ]

        try:
            res = requests.get(self.tenor_api_url, params=params)
            if res.status_code != 200:
                raise Exception('Unable to get GIF for ' + ' '.join(arg))
        except Exception as ex:
            print(ex)
            await ctx.send(ex)
        else:
            obj = json.loads(res.text, object_hook=lambda o: SimpleNamespace(**o))
            results = obj.results
            result = results[random.randrange(0, len(results))]
            if result != None:
                embed = discord.Embed()
                embed.set_image(url=result.media[0].gif.url)
                embed.set_footer(text='via Tenor', icon_url='https://www.gstatic.com/tenor/web/attribution/PB_tenor_logo_blue_vertical.png')
                print(f'{ctx.author.name} requested a gif.')
                await ctx.send(embed=embed)
            else:
                await ctx.send('No results exist for ' + ' '.join(arg))

    @commands.command(
        name='insult',
        help='You can insult by @mentioning someone. Good luck!'
    )
    async def insult_someone(self, ctx, arg):
        if re.compile(r'\d+').search(arg).group() == str(self.bot.user.id):
            await ctx.send(f'Hey! {ctx.author.mention}, You can\'t insult me.')
        else:
            try: 
                res = requests.get('https://evilinsult.com/generate_insult.php?lang=en&type=json')
                if res.status_code != 200:
                    raise Exception('Oops! Something went wrong.')
            except Exception as e:
                print(e)
                await ctx.send(f'{arg}, You\'re lucky.')
            else:
                await ctx.send(f'{arg} {res.json()["insult"]}')

def setup(bot):
    bot.add_cog(Garlic(bot))                  
        