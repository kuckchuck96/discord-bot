from datetime import datetime
import json
from os import name
from types import SimpleNamespace
import discord
from discord.ext import commands
import requests
from config import default


class Vaccine(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.config = default.config()

    @commands.command(
        name='vaccine',
        help='Provides Covid-19 vaccination centers based on \'pincode\' and \'date\' (dd-mm-yyyy).'
    )
    async def vaccine_availability(self, ctx, *arg):
        pincode, date = map(str, arg)

        try:
            res = requests.get(url=self.config.cowinapi.findbypin, params=[
                ('pincode', pincode),
                ('date', date)
            ])
            if res.status_code != 200:
                raise Exception('Unable to get vaccination centers.')
        except Exception as ex:
            await ctx.send(ex)
        else:
            obj = json.loads(res.text, object_hook=lambda o: SimpleNamespace(**o))

            if len(obj.sessions) > 0:
                # embed = discord.Embed(
                #     title=f'Vaccination centers near {pincode} as of {date}',
                #     colour=discord.Color.magenta()
                # )
                # for field in ['name', 'district_name', 'block_name', 'state_name']:
                #     values = list()
                #     for sesh in obj.sessions:
                #         values.append(eval('sesh.' + field))
                #     embed.add_field(name=field.split('_')[0].capitalize(), value='\n'.join(values), inline=True)
                embeds = list()
                for sesh in obj.sessions:
                    embed = discord.Embed(
                        title=f'{sesh.name}, {sesh.district_name}',
                        description='Till ' + datetime.strptime(sesh.to, '%H:%M:%S').strftime('%I:%M %p'),
                        colour=discord.Color.magenta()
                    )
                    # values = list()
                    # for field in ['fee_type', 'available_capacity', 'min_age_limit', 'vaccine', 'slots']:
                    #     embed.add_field(name=' '.join(i for i in field.split('_')).capitalize(), value=eval(f'sesh.{field}'), inline=True)
                    embed.add_field(name='Fee type', value=sesh.fee_type, inline=True)
                    embed.add_field(name='Capacity', value=sesh.available_capacity, inline=True)
                    embed.add_field(name='Age limit', value=f'{sesh.min_age_limit}+', inline=True)
                    embed.add_field(name='Brand', value=sesh.vaccine, inline=True)
                    embed.add_field(name='Time slots', value='\n'.join(t for t in sesh.slots), inline=True)
                    embeds.append(embed)
                for e in embeds:
                    await ctx.send(embed=e)
            else:
                await ctx.send(f'Sorry! No vaccination centers available near {pincode} on {date}.')



def setup(bot):
    bot.add_cog(Vaccine(bot)) 