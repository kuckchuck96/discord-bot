import asyncio
import re
import discord
import youtube_dl
from datetime import datetime
import math

from discord.ext import commands, tasks

from utils.Helper import Helper

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0', # bind to ipv4 since ipv6 addresses cause issues sometimes,
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.webpage_url = data.get('webpage_url')
        self.thumbnail = data.get('thumbnail')
        self.views = data.get('view_count')
        self.rating = data.get('average_rating')
        self.upload_date = data.get('upload_date')
        self.upload_by = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        self.duration = data.get('duration')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.songs_list = []
        self.helper = Helper(bot)

    async def embed_stream(self, ctx, player):
        # Embeds have 1024 char limit
        # playing_title = f'[{player.title}]({player.webpage_url})'[0:1024] 

        embed = discord.Embed(
            name = 'LASNBot Music',
            # title = 'Now Playing',
            title = player.title,
            color = discord.Color.dark_red(),
            timestamp = datetime.strptime(datetime.strptime(player.upload_date, '%Y%m%d').strftime('%d/%m/%Y'), '%d/%m/%Y'),
            url = player.webpage_url
        )
        embed.set_thumbnail(url= player.thumbnail)
        embed.add_field(name='Rating', value='⭐' * math.floor(player.rating))
        embed.add_field(name='Views', value=player.views)
        embed.add_field(name='Duration', value=f'{round(int(player.duration)/60, 1)} mins')
        # embed.add_field(name= '\u200b', value= playing_title)  
        embed.set_author(name=player.upload_by, url=player.uploader_url)

        msg = await ctx.send(embed=embed) 
        await msg.add_reaction('🧑‍🎤')

    @commands.command(name = 'join',
        aliases = ['aaja'],
        help = 'Ask LASN to grace us with his company')
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        #To Join Voice Channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()

    @commands.command(name = 'stream',
        aliases = ['baja', 'play'],
        help = 'Stream music from youtube')
    async def stream(self, ctx, *, url):
        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        self.songs_list.append(player)
        self.ctx = ctx

        if all([not self.monitor.is_running(), not ctx.voice_client.is_playing(), not ctx.voice_client.is_paused()]):
            self.monitor.start()

    async def play_song(self, ctx, player):
        async with ctx.typing():
            # player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

            # Change bot presence.
            await self.helper.change_bot_presence(activity=discord.ActivityType.playing, name=player.title)
        await self.embed_stream(ctx, player)

    @commands.command(name = 'pause',
        aliases = ['pse'],
        help = 'Pause currently playing music')
    async def pause(self,ctx):
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")
        await ctx.message.add_reaction('⏯')    
        ctx.voice_client.pause()

    @commands.command(name = 'resume',
        aliases = ['rs'],
        help = 'Resume music that is currently paused')
    async def resume(self,ctx):
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")
        await ctx.message.add_reaction('⏯')    
        ctx.voice_client.resume()

    @commands.command(
        help='Jump to the next song if any.'
    )
    async def next(self, ctx):
        if ctx.voice_client is not None:
            ctx.voice_client.stop() if len(self.songs_list) > 0 else await ctx.send('No queued songs found!')

    @commands.command(
        name='queue',
        help='Get queued songs.'
    )
    async def get_queue(self, ctx):
        await ctx.send(
            f'Up Next ⏭️ **{self.songs_list[0].title}**' if len(self.songs_list) == 1 else '\n'.join([f'{i + 1}\u20E3 **{s.title}**'  for (i, s) in enumerate(self.songs_list)])
        ) if len(self.songs_list) > 0 else await ctx.send('No queued songs found!')

    @commands.command(name = 'volume',
        aliases = ['vol'],
        help = 'Change lasn ')
    async def volume(self, ctx, volume: int):
        #Change Vol
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command(help= 'Disconnect from voice channel')
    async def stop(self, ctx):
        #Remove Bot
        await ctx.message.add_reaction('🛑')
        await ctx.voice_client.disconnect()

        # Stop monitor and reset queue.
        self.songs_list = []
        self.stop_monitor()

        # Reset bot presence.
        await self.helper.change_bot_presence(activity=discord.ActivityType.listening)

    # @play.before_invoke
    #@yt.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif any([ctx.voice_client.is_playing(), ctx.voice_client.is_paused()]):
            msg = await ctx.send('Queued: **{0}**'.format(re.compile('\s+').split(ctx.message.content, 1)[1].capitalize()))
            emojis = ['⏳', f'{len(self.songs_list) + 1}\u20E3']
            for e in emojis:
                await msg.add_reaction(e)

    @tasks.loop(seconds=2.5)
    async def monitor(self):
        print('Monitor running...')
        if len(self.songs_list) > 0:
            if self.ctx is not None:
                vc = self.ctx.voice_client
                if all([not vc.is_playing(), not vc.is_paused()]):
                    player = self.songs_list.pop(0)
                    print(f'Playing: {player.title}.')

                    await self.play_song(self.ctx, player)

    def stop_monitor(self) -> None:
        if self.monitor.is_running():
            print('Stopping Monitor...')
            self.monitor.cancel()

            while self.monitor.is_being_cancelled():
                continue
            
            print('Monitor stopped!')

def setup(bot):
    bot.add_cog(Music(bot))