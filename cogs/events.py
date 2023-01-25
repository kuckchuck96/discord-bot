import discord
import utils

from discord.ext import commands
from utils import notify
from utils.Helper import Helper


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.helper = Helper(bot)

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

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        try:
            await notify.notify_game_activity(self.bot, before, after)
        except Exception as err:
            print(err)            
        
    @commands.Cog.listener()
    async def on_ready(self):
        await self.helper.change_bot_presence(activity=discord.ActivityType.listening)

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
    