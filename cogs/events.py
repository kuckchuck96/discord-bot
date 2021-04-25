import discord
import config

from discord.ext import commands
from config import default

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        config = default.config()
        self.r6stats_channel = config.r6_notify_channel

    async def embed_notification(self, after):
        embed = discord.Embed(
            name = 'LASNBot',
            title = f'{after.name} started playing Tom Clancy\'s Rainbow Six Siege',
            description = f'Join now!',
            color = discord.Color.red()
        )
        return embed    

    @commands.Cog.listener()
    async def on_connect(self):
        try:
            print('Connecting to discord...')   
        except Exception as ex:
            print(f'Discord connection error: {ex}')

    @commands.Cog.listener()
    async def on_disconnect(self):
        print(f'Disconnected from discord...reconnecting...') 

    @commands.Cog.listener()
    async def on_resumed(self):
        print(f'Reconnected to discord.')

    # @TODO: Migrate this out of here
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        try:
            if after.activity != None: #Ignore other detail events
                if (after.activity.name == "Tom Clancy's Rainbow Six Siege" or after.activity.name == "Rainbow Six Siege") and after.activity.details == None:
                    channel = self.bot.get_channel(self.r6stats_channel)
                    embed = await self.embed_notification(after)
                    await channel.send(embed=embed)
        except Exception as err:
            print(err)            
        
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name='lasangiri'))

        if self.bot.user.avatar == None:
            image_path = 'images/garlic_icon.png'
            with open(image_path, 'rb') as f:
                image = f.read()
            
            await self.bot.user.edit(avatar=image)

        print(f'{self.bot.user.name} is online | Servers: {len(self.bot.guilds)}')

    @commands.Cog.listener()
    async def on_command(self, ctx):
        print(f'[Command] {ctx.message.clean_content}')

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot == False:
            await message.channel.send(f'I see everything {message.author.mention}')  
            await message.channel.send('http://gph.is/12wV6iC') # Eye of Sauron

def setup(bot):
    bot.add_cog(Events(bot))        
    