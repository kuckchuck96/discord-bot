import datetime
import json
import discord
import config
import requests

from types import SimpleNamespace
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

    async def request_vaccine_availability(self, ctx, params):
        try:
            res = requests.get(url=self.cowin_api_url, params=params)
            if not res.ok:
                raise Exception('Unable to get vaccination centers.')
            return json.loads(res.text, object_hook=lambda o: SimpleNamespace(**o))
        except Exception as ex:
            await ctx.send(ex)

    async def add_embed_fields(self, center, session, date):
        embed = discord.Embed(
            title=f'{ center.name }, { center.district_name }, { center.state_name }',
            colour=discord.Color.magenta(),
            description='**📍Address:** {0}\n**🏢 Block name:** {1}\n🗓️ **{2}**\n'.format(center.address, center.block_name, date if len(center.block_name) else 'NA'),
        )
        embed.add_field(name='💰 Fees', value=center.fee_type)
        embed.add_field(name='🏟️ Capacity', value=session.available_capacity)
        embed.add_field(name='{0} Age'.format('👪' if session.min_age_limit <= 18 else '👨👩'), value=f'{session.min_age_limit}+')
        embed.add_field(name='💉 Vaccine', value=session.vaccine)
        embed.add_field(name='⏱️ Slots', value='\n'.join(f'{i+1}) {s}' for i, s in enumerate(session.slots)))
        embed.set_footer(text='Powered by Co-WIN Public APIs, A GoI Initiative.', icon_url='https://www.countryflags.io/in/flat/64.png')
        return embed

    async def construct_embeds(self, centers, date, week):
        incoming_date = date.split('-')
        embeds = list()
        # Iterating to match the date passed as a parameter.
        if week:
            for center in centers:
                for session in center.sessions:
                    embed = await self.add_embed_fields(center, session, date)
                    embeds.append(embed)
        else:
            for center in centers:
                for session in center.sessions:
                    if all(int(x) == int(y) for x, y in zip(incoming_date, str(session.date).split('-'))):
                        embed = await self.add_embed_fields(center, session, date)
                        embeds.append(embed)
        return embeds            


    async def render_embeds_by_date(self, ctx, centers, date, pincode):
        embeds = await self.construct_embeds(centers, date, False)
        if len(embeds):
            for e in embeds:
                await ctx.send(embed=e)
        else:
            await ctx.send(f'Sorry! No vaccination centers available near **{pincode}** on **{date}**')

    async def render_embeds_for_week(self, ctx, centers, pincode, date_now, seventh_day):
        embeds = await self.construct_embeds(centers, date_now, True)
        if len(embeds):
            for e in embeds:
                await ctx.send(embed=e)
        else:
            await ctx.send(f'Sorry! No vaccination centers available near **{pincode}** from **{date_now} - {seventh_day}**')

    async def get_7th_successive_date(self):
        date_now = datetime.date.today()
        seventh_day = date_now + datetime.timedelta(days=7)
        return { 'now': date_now.strftime("%d-%m-%Y"), 'seventh_day': seventh_day.strftime("%d-%m-%Y") }

    @commands.command(
        name='vaccine',
        help='Provides Covid-19 vaccination centers based on \'pincode\' and \'date\' (dd-mm-yyyy).'
    )
    async def vaccine_availability(self, ctx, pincode, date = ''):
        params = {
            'pincode': pincode,
            'date': date
        }
        if not len(date):
            interval = await self.get_7th_successive_date()
            date_now = interval['now']
            seventh_day = interval['seventh_day']
            params['date'] = date_now
            centers = await self.request_vaccine_availability(ctx, params)
            await ctx.send(f'Searching for sessions between **{date_now} - {seventh_day}**...')
            if len(centers):
                await self.render_embeds_for_week(ctx, centers, pincode, date_now, seventh_day)
            else:
                await ctx.send(f'Sorry! No vaccination centers available near **{pincode}** from **{date_now} - {seventh_day}**')
        else:    
            centers = await self.request_vaccine_availability(ctx, params)
            await ctx.send(f'Searching for sessions on **{date}**...')
            if len(centers):
                await self.render_embeds_by_date(ctx, centers, date, pincode)
            else:
                await ctx.send(f'Sorry! No vaccination centers available near **{pincode}** on **{date}**')

def setup(bot):
    bot.add_cog(Pandemic(bot))            