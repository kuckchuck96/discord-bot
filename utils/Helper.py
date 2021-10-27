import discord


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