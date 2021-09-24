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
import time

import inspect



class Config:
    def __init__(self, db : aiosqlite.Connection):
        self._db = db
        self.data = {}

    @property
    def db(self):
        return self._db

    async def populate(self):
        """ Populates the cache to reflect the database. Should ideally only be used once. """

        async with self._db.cursor() as cur:
            query = await cur.execute('SELECT * FROM Config LIMIT 1')
            row = await query.fetchone()

        for column in row.keys():
            self.data[column] = row[column]


    async def update(self):
        """ Updates the database to reflect the local cache. """
        async with self._db.cursor() as cur:
            for k, v in tuple(self.data.items()):
                # Usually this is a bad idea but our values aren't user defined, so we are OK here
                await cur.execute('UPDATE Config SET {0} = {1}'.format(k, v))
            await self._db.commit()

    def __getitem__(self, key):
        """ Gets an item from the local cache. """
        return self.data.get(key)

    def __setitem__(self, key, value):
        """ Sets a value in the local cache. Call `update()` to reflect it in the database. """
        self.data[key] = value

class _DBCursor:
    def __init__(self, db):
        self.cursor = None
        self.db = db

    async def __aenter__(self):
        if self.cursor is None:
            self.cursor = await self.db.cursor()
            return self.cursor

    async def __aexit__(self, *options):
        if self.cursor is not None:
            await self.cursor.close()
            self.cursor = None

initial_extensions = (
    'cogs.core',
    'cogs.afk',
    'cogs.calculator',
    'cogs.levels',
    'cogs.moderation',
    'cogs.tickets',
    'cogs.fun',
    'cogs.reddit',
    'cogs.misc',
    'cogs.logging',
    'jishaku'
)

class TBot(commands.Bot):
    def __init__(self, *, db : aiosqlite.Connection, session : aiohttp.ClientSession, config : Config, start_time : int):
        super().__init__("!", intents=discord.Intents.all())
        self.db = db
        self.session = session
        self.start_time = start_time
        self.config = config

        self.help_command = MyHelp()

        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                print(f'Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()
                
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.DisabledCommand):
            await ctx.send("That command is disabled.")
        elif isinstance(error, CommandOnCooldown):
            await ctx.send(f"Please wait {int(error.retry_after)} before using that command again.")
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        
    async def on_ready(self):
        print("------------------------------")
        print(f"Logged in as {self.user}")
        print("------------------------------")

    async def get_settings(self) -> aiosqlite.Row:
        async with self.con.cursor() as cur:
            query = await cur.execute('SELECT * FROM Settings LIMIT 1')
            row = await query.fetchone()
            return row

    def cursor(self) -> _DBCursor:
        return _DBCursor(self.db)


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
    config = Config(db)
    await config.populate()
    time = datetime.now().timestamp()

    bot = TBot(db=db, session=session, start_time=time, config=config)
    TOKEN = os.getenv('BETA_TOKEN')

    try:
        await bot.start(TOKEN)
    finally:
        await db.close()
        await session.close()

asyncio.run(main())

