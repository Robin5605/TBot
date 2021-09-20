import traceback
import discord
from discord.ext import commands
import uuid

class Moderation(commands.Cog):
    """ALL FUNCTIONALITY RELATED TO MODERATION"""

    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator

    @commands.command()
    async def warn(self, ctx : commands.Context, member : discord.Member, *, reason : str ="No reason provided."):
        async with self.bot.db.cursor() as cur:
            await cur.execute("INSERT INTO Moderation VALUES (?, ?, ?, ?)", [str(uuid.uuid4()), member.id, ctx.message.author.id, reason])
            await self.bot.db.commit()

        await ctx.send(f"Warned {member.mention}.")

    @commands.command()
    async def unwarn(self, ctx : commands.Context, warnID : str):
        async with self.bot.db.cursor() as cur:
            query = await cur.execute("SELECT * FROM Moderation WHERE warnID = ?", [warnID])
            row = await query.fetchone()
            if not row:
                await ctx.send('Invalid ID')
                return
            
            user = self.bot.get_user(row['userID'])
            await ctx.send(f'Removed {user.mention}\'s warning.')

            cur.execute('DELETE FROM Moderation WHERE warnID = ?', [warnID])
            await self.bot.db.commit()

    @commands.command()
    async def warnings(self, ctx : commands.Context, member : discord.Member):
        async with self.bot.db.cursor() as cur:
            query = await cur.execute("SELECT * FROM Moderation WHERE userID = ?", [member.id])
            row = await query.fetchall()

        embed = discord.Embed(color=0xff5858)
        if row:
            for warn in row:
                embed.add_field(
                    name=warn['warnID'],
                    value=f"""
                        Reason: {warn['reason']}
                        Moderator: {self.bot.get_user(warn['modID']).mention}
                    """,
                    inline=False
                )
        else:
            embed.description = f"No warnings for this user."

        embed.set_author(name=f"Warnings for {member}", icon_url=member.avatar)
        embed.set_footer(text=f"ID: {member.id}")

        await ctx.send(embed=embed)

    @commands.command()
    async def clearwarns(self, ctx : commands.Context, member : discord.Member):
        async with self.bot.db.cursor() as cur:
            await cur.execute("DELETE FROM Moderation WHERE userID = ?", [member.id])
            await self.bot.db.commit()
        
        await ctx.send(f"Cleared all warnings for {member.mention}.")

    @commands.command(name='ban')
    async def _ban(self, ctx : commands.Context, member : discord.Member, *, reason="No reason provided."):
        await member.ban(delete_message_days=0, reason=reason)
        await ctx.send(f"Banned {member.mention}.")

    @commands.command(name='unban')
    async def _unban(self, ctx : commands.Context, user: discord.User):
        await ctx.guild.unban(user)
        await ctx.send(f"Unbanned {user.mention}")

    @commands.command()
    async def deafen(self, ctx, member: discord.Member):
        await member.edit(deafen=True)
        await ctx.send(f"Deafened {member.mention}.")

    @commands.command()
    async def undeafen(self, ctx, member: discord.Member):
        await member.edit(deafen=False)
        await ctx.send(f"Undeafened {member.mention}")

    @commands.command()
    async def lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send("Locked this channel.")

    @commands.command()
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=None)
        await ctx.send("Unlocked this channel.")

    async def cog_command_error(self, ctx, error):
        print(f'{type(0)}: {error}')
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send("Missing required arguments.")
        elif isinstance(error, discord.Forbidden):
            await ctx.send("Sorry, I don't have permission to do that")
        elif isinstance(error, commands.errors.CheckFailure):
            await ctx.send("Sorry, you don't have the sufficient permissions to do that.")
        elif isinstance(error, commands.CommandInvokeError):
            original = error.original
            if isinstance(original, discord.Forbidden):
                await ctx.send("Sorry, I don't have permission to do that.")

def setup(bot):
    bot.add_cog(Moderation(bot))