import discord
import requests
import os
import datetime

from discord.ext import commands

def get_about_stats(stats):
    level = stats['progression']['level']
    playtime = str(datetime.timedelta(seconds=stats['stats']['general']['playtime']))
    total_xp = stats['progression']['total_xp']
    lootbox_probability = stats['progression']['lootbox_probability']
    return f'**Level:** {level}\n**Playtime:** {playtime}\n**Total XP:** {total_xp}\n**Loot Probability:** {lootbox_probability}'

def get_general_stats(stats):
    kills = stats['kills']
    deaths = stats['deaths']
    # assists = stats['assists'] Not available in all queues
    kd = stats['kd']
    wins = stats['wins']
    losses = stats['losses']
    wl = stats['wl']
    matches_played = stats['games_played']
    return f'**K/D:** {kd}\n**Kills:** {kills}\n**Deaths:** {deaths}\n**W/L:** {wl}\n**Wins:** {wins}\n**Losses:** {losses}\n**Matches Played:** {matches_played}'

def get_kills_breakdown_stats(stats):
    headshots = stats['headshots']
    blind_kills = stats['blind_kills']
    melee_kills = stats['melee_kills']
    penetration_kills = stats['penetration_kills']
    bullets_fired = stats['bullets_fired']
    bullets_hit = stats['bullets_hit']
    return f'**Headshots:** {headshots}\n**Blind Kills:** {blind_kills}\n**Melee Kills:** {melee_kills}\n**Wall Bang:** {penetration_kills}\n**Bullets Fired:** {bullets_fired}\n**Bullets Hit:** {bullets_hit}'

def get_miscellaneous_stats(stats):
    reinforcements = stats['reinforcements_deployed']
    revives = stats['revives']
    suicides = stats['suicides']
    barricades = stats['barricades_deployed']
    return f'**Reinforcements:** {reinforcements}\n**Barricades:** {barricades}\n**Revives:** {revives}\n**Suicides:** {suicides}'

def map_queue(queue, stats):
    if queue == 'casual':
        return stats['stats']['queue']['casual']
    elif queue == 'ranked':
        return stats['stats']['queue']['ranked']
    elif queue == 'other':
        return stats['stats']['queue']['other']    
    # Default 'all'            
    return stats['stats']['general']

async def embed_stats(ctx, stats, queue):
    try:
        about = get_about_stats(stats)
        mapped_queue = map_queue(queue, stats)
        general = get_general_stats(mapped_queue)
        kills_breakdown = get_kills_breakdown_stats(stats['stats']['general'])
        miscellaneous = get_miscellaneous_stats(stats['stats']['general'])
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
        await ctx.send(embed=embed)
    except Exception as err:
        print(err)
        await ctx.send('Something went wrong, finding someone to blame...')

class R6Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name = 'r6',
        aliases = ['r', 'rainbow', 'rainbow6', 'rainbowsix'],
        help = 'Get R6 stats for LASN'
    )
    async def get_stats(self, ctx, user, queue = 'all', platform = 'pc'):
        try:
            api_key = os.getenv('R6_STATS_KEY')
            requestUrl = os.getenv('R6_STATS_URL') + f'/stats/{user}/{platform}/generic'
            headers = {'Accept': 'application/json', 'Authorization': f'Bearer {api_key}'}
            statsRes = requests.get(requestUrl, headers = headers)
            if statsRes.status_code != 200:
                await ctx.send('Please check the arguments passed...')
            await embed_stats(ctx, statsRes.json(), queue)
        except Exception as err:
            print(err)   
            await ctx.send('Something went wrong, finding someone to blame...probably R6Stats')

def setup(bot):
    bot.add_cog(R6Stats(bot))             
