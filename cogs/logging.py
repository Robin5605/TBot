import typing
import discord
from discord.ext import commands

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_message_edit(self, before : discord.Message, after : discord.Message):
        self.channel = self.bot.get_channel(self.bot.config['logID'])
        if self.channel is None:
            return

        embed = discord.Embed(title='Message edited', description=f'[Jump to message]({after.jump_url} \"Jumps to the message that was edited\")', color=discord.Color.blue())
        embed.set_author(name=str(after.author), icon_url=after.author.avatar.url)
        embed.add_field(name='Before', value=before.content, inline=True)
        embed.add_field(name='After', value=after.content, inline=True)

        await self.channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message : discord.Message):
        self.channel = self.bot.get_channel(self.bot.config['logID'])
        if self.channel is None:
            return

        embed = discord.Embed(title='Message deleted', color=discord.Color.red())
        embed.set_author(name=str(message.author), icon_url=message.author.avatar.url)
        embed.add_field(name='Content', value=message.content, inline=False)

        await self.channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Logging(bot))