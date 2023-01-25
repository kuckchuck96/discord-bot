import discord
import config

from discord.ext import commands
from config import default

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        config = default.config()
        self.bot_prefix = config.bot_prefix

    @commands.command(
        name = 'help',
        help = 'You already know what this does'
    )    
    async def help(self, ctx):
        try:
            prefix = self.bot_prefix
            embed = discord.Embed(
                name = 'LASNBot',
                title = 'Commands',
                description = f'Use prefix {prefix}\n\n',
                color = discord.Color.blue()
            )
            for command in self.bot.walk_commands():
                embed.add_field(name = command.name, value = command.help)
            await ctx.send(embed=embed)
        except Exception as err:
            print(err)
            await ctx.send('Something went wrong, finding someone to blame...')

def setup(bot):
    bot.add_cog(Help(bot))        