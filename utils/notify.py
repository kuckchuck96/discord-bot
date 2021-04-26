import discord
import config

from config import default

config = default.config()

async def r6notify(bot, member):
    ''' Notify when a user starts playing R6 '''
    if member.activity != None: #Ignore other detail events
        if (member.activity.name == "Tom Clancy's Rainbow Six Siege" or member.activity.name == "Rainbow Six Siege") and member.activity.details == None:
            channel = bot.get_channel(config.r6_notify_channel)
            embed = embed_r6_notification(member)
            await channel.send(embed=embed)

def embed_r6_notification(member):
    ''' Create embed for r6 notification '''
    embed = discord.Embed(
        name = 'LASNBot',
        title = f'{member.name} started playing Tom Clancy\'s Rainbow Six Siege',
        description = f'Join now!',
        color = discord.Color.red()
    )
    return embed   