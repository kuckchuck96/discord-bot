import discord
import config
import requests

from discord.ext import commands
from config import default

class Pandemic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        config = default.config()
        self.covid_tracker_url = config.covid_tracker.api_url

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

def setup(bot):
    bot.add_cog(Pandemic(bot))            