import discord
from discord.ext import commands
import datetime
import aiosqlite

class AFK(commands.Cog):
    def __init__(self, bot : commands.Bot):
        self.bot = bot

    @commands.command()
    async def afk(self, ctx : commands.Context, *, reason : str = "AFK"):
        author : discord.Member = ctx.author
        since = round(datetime.now().timestamp())

        async with self.bot.con.cursor() as cur:
            await cur.execute("INSERT INTO AFK VALUES (?, ?, ?)", [author.id, since, reason])
            await self.con.commit()
        
        try:
            await author.edit(nick=f'[AFK] {author.nick or author.name}')
            await ctx.send(f'{ctx.author.mention}, I set your AFK status as: {reason}.')
        except discord.Forbidden:
            await ctx.send(f'{ctx.author.mention}, I couldn\'t change your nickname, but I stil set your AFK status as: {reason}.')

    @commands.Cog.listener()
    async def on_message(self, message : discord.Message):
        # Don't want other bots or this bot
        # triggering this recursively
        # Also don't want on_message
        # and afk command to be triggered at once
        if message.author.bot or message.content.startswith('$afk'):
            return

        async with self.bot.db.cursor() as cur:
            query = await cur.execute("SELECT * FROM AFK WHERE userID = ?", [message.author.id])
            row = await query.fetchall()

            if row:
                member = message.guild.get_member(row['userID'])
                since = f"<t:{row['Since']}:R>"
                reason = row['Reason']

                if member in message.mentions:
                    await message.reply(f'{member.name} is AFK: {reason} - {since}')
                    return

                try:
                    await message.author.edit(nick=message.author.nick[5:])
                except:
                    # Ignore both errors where it tries to superscript
                    # the nickname of a user that doesn't have a nickname
                    # and also ignore the error thrown when the bot doesn't
                    # have the necessary permissions to edit nicknames
                    pass

                await cur.execute('DELETE FROM AFK WHERE userID = ?', [member.id])
                await self.con.commit()

                await message.channel.send(f'Welcome back, {member.mention}! I\'ve removed your AFK status.')

def setup(bot):
    bot.add_cog(AFK(bot))