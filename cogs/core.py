import typing
import discord
from discord.ext import commands

import sys
import traceback

import datetime
import time

initial_extensions = (
    'cogs.core'
    'cogs.afk',
    'cogs.calculator',
    'cogs.levels',
    'cogs.moderation',
    'cogs.tickets',
    'cogs.fun',
    'cogs.reddit',
    'cogs.misc',
    'jishaku'
)

class CogControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def module(self, ctx : commands.Context):
        if ctx.invoked_subcommand is None:
            print('No subcommand')
    
    @module.command()
    async def reload(self, ctx : commands.Context, name : str):
        if name == 'all':
            for extension in initial_extensions:
                try:
                    ctx.bot.reload_extension(extension)
                except Exception as e:
                    await ctx.send('Failed loading an extension.')
                    print(e, file=sys.stderr)
                    traceback.print_exc()
                    return

            await ctx.send('Successfully reloaded all extensions.')
            return

        try:
            ctx.bot.reload_extension('cogs.' + name)
            await ctx.send(f'Successfully reloaded extension `{name}`')
        except commands.ExtensionNotLoaded:
            await ctx.send(f'Extension `{name}` was not loaded due to an error.')

    @module.command()
    async def load(self, ctx : commands.Context, name : str):
        if name == 'all':
            for extension in initial_extensions:
                try:
                    ctx.bot.load_extension(extension)
                except Exception as e:
                    await ctx.send('Failed loading an extension.')
                    print(e, file=sys.stderr)
                    traceback.print_exc()
                    return

            await ctx.send('Successfully loaded all extensions.')
            return

        if name == 'core':
            await ctx.send("Cannot load core modules as they are already loaded.")
            return

        try:
            ctx.bot.load_extension('cogs.' + name)
            await ctx.send(f'Successfully loaded extension `{name}`')
        except commands.ExtensionNotLoaded:
            await ctx.send(f'Extension `{name}` was not loaded due to an error.')

    @module.command()
    async def unload(self, ctx : commands.Context, name : str):
        if name == 'all':
            for extension in initial_extensions:
                try:
                    ctx.bot.unload_extension(extension)
                except Exception as e:
                    await ctx.send('Failed unloading an extension.')
                    print(e, file=sys.stderr)
                    traceback.print_exc()
                    return

            await ctx.send('Successfully unloaded all extensions.')
            return

        if name == 'core':
            await ctx.send("Cannot unload core modules.")
            return

        try:
            ctx.bot.unload_extension('cogs.' + name)
            await ctx.send(f'Successfully unloaded extension `{name}`')
        except commands.ExtensionNotLoaded:
            await ctx.send(f'Extension `{name}` was not unloaded due to an error.')

    @module.command()
    async def disable(self, ctx : commands.Context, name : str):
        command = self.bot.get_command(name)
        if command is None:
            await ctx.send("Command not found.")
            return

        command.enabled = False

        await ctx.send(f'Disabled the `{command.qualified_name}` command.')

    @module.command()
    async def enable(self, ctx : commands.Context, name : str):

        command = self.bot.get_command(name)
        if command is None:
            await ctx.send("Command not found.")
            return

        command.enabled = True

        await ctx.send(f'Enabled the `{command.qualified_name}` command.')
        
class Core(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    async def uptime(self, ctx : commands.Context):
        """ Displays the uptime of the bot. """
        delta = datetime.now().timestamp() - self.bot.start_time
        formatted = time.strftime("%H hours, %M minutes, and %S seconds", time.gmtime(delta))

        await ctx.send(f'Bot has been online for **{formatted}** seconds.')

    @commands.group()
    async def settings(self, ctx):
        if ctx.invoked_subcommand is None:
            print('No subcommand')

    @settings.command()
    async def logging(self, ctx, new : typing.Union[discord.TextChannel, typing.Literal[False]]):
        if new is False:
            self.bot.config['logID'] = 0
            await ctx.send('Turned off logging. You may turn it back on by setting its channel')
        else:
            self.bot.config['logID'] = new.id
            await ctx.send(f'Logging messages will now be sent in {new.mention}.')

        await self.bot.config.update()
            
        

def setup(bot):
    bot.add_cog(CogControl(bot))
    bot.add_cog(Core(bot))