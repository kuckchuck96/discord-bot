import asyncio
from functools import reduce
import json
from os import path
from discord.ext import commands
from discord.ext.commands import bot
import discord
import os
from gtts import gTTS
from config import default
import requests
from types import SimpleNamespace


class Social(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.config = default.config()
        self.folders = ['media', 'news']

    def create_news (self, country) -> str:
        # text = '1. Hi! My name is Kunal Deshpande.'
        # Fetch news and convert to string.
        try:
            res = requests.get(url=self.config.news.api_url, params=[
                ('country', country),
                ('apiKey', self.config.news.api_key)
            ])

            if res.status_code != 200:
                raise Exception('Unable to fetch news from source.')
        except Exception as ex:
            print(ex)
            return None
        else:
            obj = json.loads(res.text, object_hook=lambda o: SimpleNamespace(**o))            

            # Prepare news.
            content = '\n'.join(['Today\'s top 5 news.']+ [f'{i + 1}. {n.title}' for i, n in enumerate(obj.articles) if i < 5] + [f'{self.bot.user.name} over and out!'])

            # folders = ['media', 'news']
            path = os.path.join(os.getcwd(), *self.folders)
            if not os.path.isdir(path):
                os.makedirs(path)
            media = gTTS(text=content, lang='en', slow=False, tld='co.in')
            file_to_create = os.path.join(path, 'news.mp3')
            media.save(file_to_create)
            return file_to_create 

    @commands.command(
        help='Connect to the author\'s voice channel and speaks most trending news.'
    )
    async def news(self, ctx, arg):
        connect = ctx.author.voice
        if connect:
            vc = await connect.channel.connect()
            # Create and store news audio files.
            audio_file = self.create_news(arg)
            if audio_file != None:
                src = discord.FFmpegPCMAudio(audio_file)
                if all([vc != None, src != None]):
                    vc.play(src)
                    while vc.is_playing():
                        await asyncio.sleep(1.0)
            else:
                await ctx.send('Unable to fetch news from source.')
            await vc.disconnect()
            try:
                if os.path.isfile(audio_file):
                    os.remove(audio_file)
                    os.removedirs(os.path.join(*self.folders))
            except OSError as err:
                print('Unable to cleanup file storage.')
        else:
            await ctx.send(f'{ctx.author.mention}, you must be connected to the voice channel.')

    # @commands.command(
    #     name='bye',
    #     aliases=['b', 'leave'],
    #     help='This command disconnects the bot from voice channel.'
    # )
    # async def leave(self, ctx):
    #     try:
    #         vc = reduce(lambda c: c.channel == ctx.author.voice.channel, self.bot.voice_clients)
    #     except Exception as ex:
    #         print(ex)
    #         await ctx.send(f'{self.bot.user.name} is not connected to any voice channel.')
    #     else:
    #         if vc != None and any([i.name == vc.channel.name for i in ctx.message.guild.voice_channels]):
    #             # print(any([i.name == vc.channel.name for i in ctx.message.guild.voice_channels]))
    #             # print(vc.channel)
    #             # print(ctx.message.guild.voice_channels[0].name)
    #             # curr_channel = reduce(lambda x: )
    #             # print(ctx.message.guild)
    #             await ctx.message.guild.voice_client.disconnect()


def setup(bot):
    bot.add_cog(Social(bot)) 
