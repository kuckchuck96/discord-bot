import discord
import config

from discord.enums import ActivityType
from config import default

config = default.config()

async def send_notification_to_channel(bot, member):
    ''' Get channel and send embed ''' 
    channel = bot.get_channel(config.r6_notify_channel)
    embed = embed_notification(member)
    await channel.send(embed=embed)

def embed_notification(member):
    ''' Create embed for game notification '''
    embed = discord.Embed(
        name = 'LASNBot',
        title = f'{member.name} started playing {member.activity.name}',
        color = discord.Color.red()
    )
    return embed   

async def notify_game_activity(bot, before, after):
    ''' Notify game activity to configured channel '''
    if before.activity and before.activity.type != ActivityType.playing:
        return None

    if after.activity and after.activity.type != ActivityType.playing:
        return None    

    if not before.activity and after.activity and after.activity.type == ActivityType.playing:
        # Add start playing logic like DB update for roulette
        print(f'[Event] {before} > playing > {after.activity.name}')  
        await send_notification_to_channel(bot, after)

    if before.activity and before.activity.type == ActivityType.playing and not after.activity:
        # Add stop playing logic like DB update for roulette
        print(f'[Event] {before} > stopped playing')                  
