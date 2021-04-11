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

    @commands.command(
        name='slotmachine',
        aliases=['slots'],
        help='Pull the lever of the invisible SLOT MACHINE'
    )       
    async def slot_machine(self, ctx):
        emojis = "🍎🍊🍐🍋🍉🍇🍓🍒"
        a = random.choice(emojis)
        b = random.choice(emojis)
        c = random.choice(emojis)

        user = f"**[ {a} {b} {c} ]\n{ctx.author.name}**,"

        if (a == b == c):
            await ctx.send(f"{user} You won! 🎉")
        elif (a == b) or (a == c) or (b == c):
            await ctx.send(f"{user} not good enough, sucker! 🖕")
        else:
            await ctx.send(f"{user} 😢")        

def setup(bot):
    bot.add_cog(Games(bot)) 