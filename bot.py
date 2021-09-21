import asyncio
import discord

from discord.ext import (
    commands,
    tasks
)

from typing import (
    List,
    Literal,
    Mapping,
    Optional, Tuple
)

from discord.ext.commands import *


import aiosqlite
import aiohttp

import uuid
import os
from datetime import datetime
from textwrap import dedent
import traceback
import sys

import inspect

initial_extensions = (
    'cogs.afk',
    'cogs.calculator',
    'cogs.levels',
    'cogs.moderation',
    'cogs.tickets',
    'cogs.fun',
    'cogs.reddit',
    'cogs.misc'
)

class TBot(commands.Bot):
    def __init__(self, *, db : aiosqlite.Connection, session : aiohttp.ClientSession):
        super().__init__("!", intents=discord.Intents.all())
        self.db = db
        self.session = session

        self.help_command = MyHelp()
        self.add_cog(CogControl(self))

        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                print(f'Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()
                
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.DisabledCommand):
            await ctx.send("That command is disabled.")
        
    async def on_ready(self):
        print("------------------------------")
        print(f"Logged in as {self.user}")
        print("------------------------------")

    async def get_settings(self) -> aiosqlite.Row:
        async with self.con.cursor() as cur:
            query = await cur.execute('SELECT * FROM Settings LIMIT 1')
            row = await query.fetchone()
            return row

class CogControl(commands.Cog):
    def __init__(self, bot : Bot):
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
        except ExtensionNotLoaded:
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

        try:
            ctx.bot.load_extension('cogs.' + name)
            await ctx.send(f'Successfully loaded extension `{name}`')
        except ExtensionNotLoaded:
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

        try:
            ctx.bot.unload_extension('cogs.' + name)
            await ctx.send(f'Successfully unloaded extension `{name}`')
        except ExtensionNotLoaded:
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
        
    
class MyHelp(commands.HelpCommand):
    def defaultFormat(self, parameter : inspect.Parameter) -> str:
        isRequired = parameter.default is inspect.Parameter.empty # No default argument = required
        return f'<{parameter.name}>' if isRequired else f'[{parameter.name}]'

    def get_command_signature(self, command : commands.Command) -> str:
        signatures = [self.defaultFormat(parameter) for parameter in command.clean_params.values()]
        
        if signatures: # Command has arguments
            return f"{self.context.prefix}{command.name} {' '.join(signatures)}"
        else:
            return f'{self.context.prefix}{command.name}'
        

    async def send_bot_help(self, mapping : Mapping[Optional[commands.Cog], List[commands.Command]]):  
        embed = discord.Embed(title='Help on Commands', description='`$help <command>` for more help.', color=discord.Color.gold())
        for cog, commands in mapping.items():
            name = cog.qualified_name if cog else 'No category'
            value = ' '.join([f'`{command.qualified_name}`' for command in commands])
            embed.add_field(name=name, value=value)
        
        channel : discord.abc.Messageable = self.get_destination()
        await channel.send(embed=embed)
    
    async def send_command_help(self, command : commands.Command):
        ctx : commands.Context = self.context
        help = f"""
        ```
        Syntax
        {self.get_command_signature(command)}
        ```
        {command.help}
        """
        embed = discord.Embed(title=f"${command.qualified_name}", description=dedent(help), color = discord.Color.gold())
        
        await ctx.send(embed=embed)

async def main():
    db = await aiosqlite.connect('bot.db')
    db.row_factory = aiosqlite.Row

    session = aiohttp.ClientSession()

    bot = TBot(db=db, session=session)
    TOKEN = os.getenv('BETA_TOKEN')

    try:
        await bot.start(TOKEN)
        #WE HAVE INSPECTED YOUR CODE
        #removing this line would break it :)
    finally:
        await db.close()
        await session.close()


asyncio.run(main())

