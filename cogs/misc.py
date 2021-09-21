import typing
import discord
from discord import embeds
from discord.ext import commands

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_delete : discord.Message = None
        self.last_edit : discord.Message = None

    @commands.Cog.listener()
    async def on_message_delete(self, message : discord.Message):
        self.last_delete = message

    @commands.Cog.listener()
    async def on_message_edit(self, before : discord.Message, after : discord.Message):
        self.last_edit = before

    @commands.command()
    async def snipe(self, ctx : commands.Context):
        """ Finds the last deleted message and sends it. """
        embed = discord.Embed(color=discord.Color.blurple())
        if self.last_delete:
            embed.description = self.last_delete.content
        else:
            embed.description = 'Nothing to snipe.'
        await ctx.send(embed=embed)

    @commands.command()
    async def editsnipe(self, ctx : commands.Context):
        """ Finds the last edited message and sends it. """
        embed = discord.Embed(color=discord.Color.blurple())
        if self.last_edit:
            embed.description = self.last_edit.content
        else:
            embed.description = 'Nothing to edit snipe.'
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Misc(bot))