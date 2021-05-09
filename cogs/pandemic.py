from datetime import datetime
import json
from types import SimpleNamespace
import discord
from requests.api import head
import config
import requests

from discord.ext import commands
from config import default

class Pandemic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        config = default.config()
        self.covid_tracker_url = config.covid_tracker.api_url
        self.cowin_api_url = config.cowinapi.findbypin

    async def embed_content(self, ctx, content):
        # Create embed
        embed = discord.Embed(
            name = 'Covid19',
            title = 'COVID19 Tracker',
            color = discord.Color.green()
        )
        if (type(content) == list):
            for item in content:
                value = self.format_data(item)
                embed.add_field(name= item['country'], value=value)
            await ctx.send(embed=embed)
        else:
            value = self.format_data(content)
            embed.set_thumbnail(url= content['countryInfo']['flag'])
            embed.add_field(name= content['country'], value=value)
            await ctx.send(embed=embed)    
            
    def format_data(self, data):
        cases = data['cases']
        deaths = data['deaths']
        today_cases = data['todayCases']
        today_deaths = data['todayDeaths']
        recovered = data['recovered']
        tests = data['tests']
        population = data['population']
        return f'**Cases:** {cases:,}\n**Deaths:** {deaths:,}\n**Cases Today:** {today_cases}\n**Deaths Today:** {today_deaths}\n**Recovered:** {recovered:,}\n**Tests:** {tests:,}\n**Population:** {population:,}'    

    async def get_data_by_country(self, country):
        data = requests.get(f'{self.covid_tracker_url}/countries/{country}')
        return data.json()

    async def get_most_affected_countries(self, limit= 10): 
        countries = requests.get(f'{self.covid_tracker_url}/countries?sort=cases')
        countries = countries.json()
        if limit == 0:
            return countries
        return countries[:limit]      

    @commands.command(
        name = 'covid',
        help = 'Track Covid19 pandemic'
    )
    async def covid_tracker(self, ctx, country = None):
        try:
            if country == 'all' or country == None:
                data = await self.get_most_affected_countries(24)
                return await self.embed_content(ctx, data)
            #Country specific data
            data = await self.get_data_by_country(country)
            return await self.embed_content(ctx, data)
        except Exception as err:
            print(err)
            await ctx.send('Something went wrong, finding someone to blame...')      

    @commands.command(
        name='vaccine',
        help='Provides Covid-19 vaccination centers based on \'pincode\' and \'date\' (dd-mm-yyyy).'
    )
    async def vaccine_availability(self, ctx, *arg):
        pincode, date = map(str, arg)

        params = {
            'pincode': pincode,
            'date': date
        }

        headers = {
            'User-Agent':  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        }

        try:
            res = requests.get(url=self.cowin_api_url, params=params, headers=headers)
            
            if not res.ok:
                raise Exception('Unable to get vaccination centers.')
        except Exception as ex:
            await ctx.send(ex)
        else:
            obj = json.loads(res.text, object_hook=lambda o: SimpleNamespace(**o))

            if len(obj.sessions) > 0:
                embeds = list()
                for sesh in obj.sessions:
                    embed = discord.Embed(
                        title=f'{sesh.name}, {sesh.district_name}',
                        description='Till ' + datetime.strptime(sesh.to, '%H:%M:%S').strftime('%I:%M %p'),
                        colour=discord.Color.magenta()
                    )
                    for field in ['fee_type', 'available_capacity', 'min_age_limit', 'vaccine', 'slots']:
                        embed.add_field(
                            name=' '.join(field.split('_')).capitalize(), 
                            value=eval('sesh.' + field) if type(eval(f'sesh.{field}')).__name__ != 'list' else '\n'.join(eval('sesh.' + field)), 
                            inline=True)
                    embeds.append(embed)

                for e in embeds:
                    await ctx.send(embed=e)
            else:
                await ctx.send(f'Sorry! No vaccination centers available near {pincode} on {date}.') 

def setup(bot):
    bot.add_cog(Pandemic(bot))            