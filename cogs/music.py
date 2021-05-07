import asyncio
import discord
import youtube_dl

from discord.ext import commands

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
        self.thumbnail = data.get('thumbnail')

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

    async def embed_stream(self, ctx, player):
        # Embeds have 1024 char limit
        playing_title = f'[{player.title}]({player.url})'[0:1024] 
        embed = discord.Embed(
            name = 'LASNBot',
            title = 'Now Playing',
            color = discord.Color.dark_red()
        )
        embed.set_thumbnail(url= player.thumbnail)
        embed.add_field(name= '\u200b', value= playing_title)  
        await ctx.send(embed=embed)     

    @commands.command(name = 'join',
        aliases = ['aaja'],
        help = 'Ask LASN to grace us with his company')
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        #To Join Voice Channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()

    @commands.command(name = 'stream',
        aliases = ['baja'],
        help = 'Stream music from youtube')
    async def stream(self, ctx, *, url):
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
        await self.embed_stream(ctx, player)

    @commands.command(name = 'pause',
        aliases = ['pse'],
        help = 'Pause currently playing music')
    async def pause(self,ctx):
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")
        ctx.voice_client.pause()
        await ctx.send(f'Paused')

    @commands.command(name = 'resume',
        aliases = ['rs'],
        help = 'Resume music that is currently paused')
    async def resume(self,ctx):
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")
        ctx.voice_client.resume()

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
        await ctx.voice_client.disconnect()

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
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

def setup(bot):
    bot.add_cog(Music(bot)) 