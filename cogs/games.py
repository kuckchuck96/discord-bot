import random
from discord.ext import commands

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help='Toss a coin to decide your fate (H: head, T: tail).'
    )
    async def toss(self, ctx, arg):
        if int(arg) in [0, 1]:
            await ctx.send(f'Head! {ctx.author.mention} wins 🎉.' if random.choice([0, 1]) == int(arg) else f'Tera naseeb kharab hai {ctx.author.mention} 😟.')
            await ctx.send('#Note: This is not a coin from famous movie "Sholay".')

def setup(bot):
    bot.add_cog(Games(bot)) 