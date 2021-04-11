import os
import requests
import random
import re

from discord.ext import commands

class Garlic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='s',
        help='Greets the user using whatever argument passed.',
        )
    async def salute(self, ctx, arg):
        await ctx.send('{0}! {1}'.format(arg, ctx.author.mention))

    @commands.command(
        name='g',
        help='Send GIFs based on the search text passed.'
        )
    async def send_gif(self, ctx, arg):
        body = [
            ('api_key', os.getenv('GIFY_API_KEY')),
            ('q', arg),
            ('limit', 50),
            ('lang', 'en'),
            ('rating', 'pg-13')
        ]
        res = requests.get(os.getenv('GIFY_API_URL'), params=body)
        if res.status_code != 200:
            await ctx.send('Oops! Something went wrong. Please try again.')
        elif len(res.json()['data']) > 0:
            gif = res.json()['data'][random.randrange(0, len(res.json()['data']))]
            await ctx.send(gif['embed_url'])
        else:
            await ctx.send('No results found for keyword "{0}".'.format(arg))

    @commands.command(
        name='num',
        help='Gives random number facts.'
    )
    async def number_trivia(self, ctx):
        res = requests.get('http://numbersapi.com/random/trivia')
        if res.status_code != 200:
            await ctx.send('Oops! Something went wrong. Please try again.')
        else:
            await ctx.send(res.text)

    @commands.command(
        name='cn',
        help='Retrieve a random chuck joke.'
    )
    async def chuck_norris(self, ctx):
        res = requests.get('https://api.chucknorris.io/jokes/random')
        if res.status_code != 200:
            await ctx.send('Oops! Something went wrong. Please try again.')
        else:
            data = res.json()
            for i in ['icon_url', 'value']:
                await ctx.send(data[i])

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
            await ctx.send(f"{user} not good enough, sucker! 🎉")
        else:
            await ctx.send(f"{user} wah wah wah 😢")

    @commands.command(
        name='insult',
        help='You can insult by @mentioning someone. Good luck!'
    )
    async def insult_someone(self, ctx, arg):
        if re.compile(r'\d+').search(arg).group() == str(self.bot.user.id):
            await ctx.send(f'Hey! {arg}, You can\'t insult me.')
        else:
            try: 
                res = requests.get('https://evilinsult.com/generate_insult.php?lang=en&type=json')
                if res.status_code != 200:
                    raise Exception('Oops! Something went wrong.')
            except Exception as e:
                print(e)
                await ctx.send(f'{arg}, You\'re lucky.')
            else:
                await ctx.send(f'{arg} {res.json()["insult"]}')

def setup(bot):
    bot.add_cog(Garlic(bot))                  
        