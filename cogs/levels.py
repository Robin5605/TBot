import discord
from discord.ext import commands
from discord.ext import tasks
import asyncio
import aiosqlite

class Levelling(commands.Cog):
    def __init__(self, bot : commands.Bot):
        self.bot = bot
        self.cache : dict[int, int] = {}
        self.lock = asyncio.Lock()
        self.bulker.start()

    async def _update_database(self):
        async with self.bot.db.cursor() as cur:
            iter = [{'id': id, 'xp': xp} for id, xp in self.cache.items()]
            await cur.executemany("""
                INSERT INTO Level
                VALUES (:id, :xp)
                ON CONFLICT(userID) DO UPDATE SET XP = XP + :xp WHERE userID = :id;
            """, iter)
            await self.bot.db.commit()

    @tasks.loop(seconds=10)
    async def bulker(self):
        async with self.lock:
            await self._update_database()
        self.cache = {}

    @bulker.after_loop
    async def on_bulker_cancel(self):
        if self.bulker.is_being_cancelled():
            await self._update_database()

    # Calculate the XP
    async def get_xp(self, member : discord.Member):
        """ Returns the `discord.Member`'s current XP from the database or cache, or 0 if the user hasn't talked yet. """

        cache_xp = self.cache.get(member.id)
        if cache_xp:
            return cache_xp

        async with self.bot.db.cursor() as cur:
            q = await cur.execute('SELECT * FROM Level WHERE userID = ?', [member.id])
            row = await q.fetchone()
            database_xp = row['XP'] if row else 0

            return database_xp

    @commands.Cog.listener()
    async def on_message(self, message : discord.Message):
        if message.author.bot:
            return

        xp = await self.get_xp(message.author)
        if xp % 100 == 0 and xp != 0:
            await message.channel.send(f'{message.author.mention} just reached level {xp / 100}. Nice job!')

        xp_per_message = 1
        try: 
            self.cache[message.author.id] += xp_per_message
        except KeyError:
            self.cache[message.author.id] = xp_per_message

        
    @commands.command()
    async def level(self, ctx : commands.Context, member : discord.Member = None):
        member = member or ctx.author

        xp_per_level = 100
        xp = await self.get_xp(member)
        level = int(xp / xp_per_level)
        xp_to_next = xp % xp_per_level


        text = f'Level: {level} | {xp_to_next}/{xp_per_level} {round((xp_to_next/xp_per_level) * 100)}%'
        embed = discord.Embed(title=f'{member}\'s level', description=text, color = discord.Color.blue())

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Levelling(bot))