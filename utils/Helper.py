import discord
import math


class Helper:
    def __init__(self, bot) -> None:
        self.bot = bot

    def change_bot_presence(self, status=discord.Status.online, activity=discord.ActivityType.listening, name='lasangiri'):
        # Changing the activity of bot.
        return self.bot.change_presence(
            status=status,
            activity=discord.Activity(
                type=activity,
                name=name
            )
        )
    
    def convert_views(views) -> str:
        pos = {
            'K': int(math.pow(10, 3)),
            'M': int(math.pow(10, 6)),
            'B': int(math.pow(10, 9)),
            'T': int(math.pow(10, 12))
        }

        return list(filter(lambda x: int(x[:-1]) > 0, [f'{views // pos[i]}{i}' for i in pos.keys()]))[-1]