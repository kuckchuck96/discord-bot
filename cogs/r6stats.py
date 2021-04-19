import discord
import requests
import os
import datetime
import config

from discord.ext import commands
from config import default

    
    
class R6Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        config = default.config()
        self.r6stats_key = config['r6stats']['api_key']
        self.r6stats_url = config['r6stats']['api_url']

    def get_about_stats(self, stats):
        level = stats['progression']['level']
        playtime = str(datetime.timedelta(seconds=stats['stats']['general']['playtime']))
        total_xp = stats['progression']['total_xp']
        lootbox_probability = stats['progression']['lootbox_probability']
        return f'**Level:** {level}\n**Playtime:** {playtime}\n**Total XP:** {total_xp}\n**Loot Probability:** {lootbox_probability}'

    def get_general_stats(self, stats):
        kills = stats['kills']
        deaths = stats['deaths']
        # assists = stats['assists'] Not available in all queues
        kd = stats['kd']
        wins = stats['wins']
        losses = stats['losses']
        wl = stats['wl']
        matches_played = stats['games_played']
        return f'**K/D:** {kd}\n**Kills:** {kills}\n**Deaths:** {deaths}\n**W/L:** {wl}\n**Wins:** {wins}\n**Losses:** {losses}\n**Matches Played:** {matches_played}'

    def get_kills_breakdown_stats(self, stats):
        headshots = stats['headshots']
        blind_kills = stats['blind_kills']
        melee_kills = stats['melee_kills']
        penetration_kills = stats['penetration_kills']
        bullets_fired = stats['bullets_fired']
        bullets_hit = stats['bullets_hit']
        return f'**Headshots:** {headshots}\n**Blind Kills:** {blind_kills}\n**Melee Kills:** {melee_kills}\n**Wall Bang:** {penetration_kills}\n**Bullets Fired:** {bullets_fired}\n**Bullets Hit:** {bullets_hit}'

    def get_miscellaneous_stats(self, stats):
        reinforcements = stats['reinforcements_deployed']
        revives = stats['revives']
        suicides = stats['suicides']
        barricades = stats['barricades_deployed']
        return f'**Reinforcements:** {reinforcements}\n**Barricades:** {barricades}\n**Revives:** {revives}\n**Suicides:** {suicides}'

    def map_queue(self, queue, stats):
        if queue == 'casual' or queue == 'unranked':
            return stats['stats']['queue']['casual']
        elif queue == 'ranked':
            return stats['stats']['queue']['ranked']
        elif queue == 'other':
            return stats['stats']['queue']['other']    
        # Default 'all'            
        return stats['stats']['general']

    async def get_stats(self, ctx, user, platform = 'pc', stat_type = 'generic'):
        api_key = self.r6stats_key
        request_url = f'{self.r6stats_url}/stats/{user}/{platform}/{stat_type}'
        headers = {'Accept': 'application/json', 'Authorization': f'Bearer {api_key}'}
        stats_res = requests.get(request_url, headers = headers)
        if stats_res.status_code != 200:
            await ctx.send('Please check the arguments passed...')
        return stats_res.json()       

    async def get_top_operators(self, operators, limit = '5'):
        #Sort operators by kills
        operators = sorted(operators['operators'], reverse=True, key=lambda g: int(g['kills']))
        if limit == 0:
            return operators
        return operators[:limit]    

    async def embed_stats(self, ctx, stats, queue, top_operators):
        try:
            about = self.get_about_stats(stats)
            mapped_queue = self.map_queue(queue, stats)
            general = self.get_general_stats(mapped_queue)
            kills_breakdown = self.get_kills_breakdown_stats(stats['stats']['general'])
            miscellaneous = self.get_miscellaneous_stats(stats['stats']['general'])
            # Create embed
            embed = discord.Embed(
                name = 'LASN Stats',
                title = 'Stats',
                color = discord.Color.blue()
            )
            embed.set_thumbnail(url= stats['avatar_url_256'])
            embed.set_author(name= stats['username'], icon_url= stats['avatar_url_146'])
            embed.add_field(name= 'About', value= about)
            embed.add_field(name= f'General({queue.capitalize()})', value= general)
            embed.add_field(name= 'Kills Breakdown', value= kills_breakdown)
            embed.add_field(name= 'Miscellaneous', value= miscellaneous)
            top5_operators = ''
            for ops in top_operators:
                name = ops['name']
                kills =  ops['kills']
                top5_operators += f'**{name}:** {kills}\n'
            embed.add_field(name= 'Top Operators', value= top5_operators)    
            await ctx.send(embed=embed)
        except Exception as err:
            print(err)
            await ctx.send('Something went wrong, finding someone to blame...')

    async def embed_operator_stats(self, ctx, user, platform):
        try:
            stats = await self.get_stats(ctx, user, platform, 'operators')
            top_operators = await self.get_top_operators(stats, 12)
            # Create embed
            embed = discord.Embed(
                name = 'LASN OP Stats',
                title = 'Operator Stats',
                color = discord.Color.blue()
            )       
            embed.set_thumbnail(url= stats['avatar_url_256'])
            embed.set_author(name= stats['username'], icon_url= stats['avatar_url_146'])
            for op in top_operators:
                name = op['name']
                kills = op['kills']
                kd = op['kd']
                wins = op['wins']
                headshots = op['headshots']
                value = f'**Kills:** {kills}\n**K/D:** {kd}\n**Wins:** {wins}\n**Headshots:** {headshots}'
                embed.add_field(name= name, value= value, inline= True)
            await ctx.send(embed=embed)
        except Exception as err:
            print(err)
            await ctx.send('Something went wrong, finding someone to blame...')    

    @commands.command(
        name = 'r6',
        aliases = ['r', 'rainbow', 'rainbow6', 'rainbowsix'],
        help = 'Get R6 stats for LASN'
    )
    async def get_r6_stats_by_user(self, ctx, user, queue = 'all', platform = 'pc'):
        try:
            queue = queue.lower()
            valid_queues = ['all', 'ranked', 'casual', 'unranked', 'other']
            valid_ops_commands = ['ops', 'operator', 'operators']
            # Operator stats
            if queue in valid_ops_commands:
                await self.embed_operator_stats(ctx, user, platform)
            else:
                # Combined stats
                if queue not in valid_queues:
                    queue = 'all'
                generic_stats = await self.get_stats(ctx, user, platform, 'generic')
                operator_stats = await self.get_stats(ctx, user, platform, 'operators')
                top_operators = await self.get_top_operators(operator_stats, 5)
                await self.embed_stats(ctx, generic_stats, queue, top_operators)
        except Exception as err:
            print(err)   
            await ctx.send('Something went wrong, finding someone to blame...probably R6Stats')

def setup(bot):
    bot.add_cog(R6Stats(bot))             
