import discord
import config

from discord.enums import ActivityType
from config import default

config = default.config()

async def r6notify(bot, member):
    ''' Notify when a user starts playing R6 '''
    if member.activity != None: #Ignore other detail events
        if (member.activity.name == "Tom Clancy's Rainbow Six Siege" or member.activity.name == "Rainbow Six Siege") and member.activity.details == None:
            channel = bot.get_channel(config.r6_notify_channel)
            embed = embed_notification(member)
            await channel.send(embed=embed)

async def send_notification_to_channel(bot, member):
    ''' Send notification to configured channel ''' 
    channel = bot.get_channel(config.r6_notify_channel)
    embed = embed_notification(member)
    await channel.send(embed=embed)

async def notify_on_playing(bot, before, after):
    if before.activity and before.activity.type != ActivityType.playing:
        return None

    if after.activity and after.activity.type != ActivityType.playing:
        return None    

    if not before.activity and after.activity and after.activity.type == ActivityType.playing:
        # Add start playing logic like DB update for roulette
        print(f'{before} > playing > {after.activity.name}')  
        await send_notification_to_channel(bot, after)

    if before.activity and before.activity.type == ActivityType.playing and not after.activity:
        # Add stop playing logic like DB update for roulette
        print(f'{before} > stopped playing')                  

def embed_notification(member):
    ''' Create embed for game notification '''
    embed = discord.Embed(
        name = 'LASNBot',
        title = f'{member.name} started playing {member.activity.name}',
        # description = f'Join now!',
        color = discord.Color.red()
    )
    return embed   