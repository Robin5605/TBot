import asyncio
import discord
from discord.ext import commands
import aiosqlite

class TicketView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None) # Persistent
        self.bot = bot

    def member_to_channel(self, member : discord.Member):
        """ Converts a `discord.Member` to a valid channel name. """
        return str(member).replace(' ', '-').replace('#', '-')

    @discord.ui.button(label='Open a ticket', style=discord.ButtonStyle.green, emoji='🎫', custom_id='TICKET_CREATE')
    async def TicketButton(self, button : discord.ui.Button, interaction : discord.Interaction):
        async with self.bot.db.cursor() as cur:
            q = await cur.execute('SELECT * FROM Tickets WHERE userID = ?', [interaction.user.id])
            row = await q.fetchone()

            if row:
                channel = interaction.guild.get_channel(row['channelID'])
                await interaction.response.send_message(f'You already have an open ticket ({channel.mention})', ephemeral=True)
                return

            channel = await interaction.guild.create_text_channel(self.member_to_channel(interaction.user))
            await channel.send(content='Actions', view=TicketActions(self.bot))

            await cur.execute('INSERT INTO Tickets VALUES (?, ?)', [interaction.user.id, channel.id])
            await self.bot.db.commit()

class TicketActions(discord.ui.View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        
    @discord.ui.button(label='Claim', style=discord.ButtonStyle.green, custom_id='TICKET_CLAIM')
    async def claim(self, button : discord.ui.Button, interaction : discord.Interaction):
        await interaction.channel.send(f'')
        await interaction.channel.edit(topic=f'Claimed by {interaction.user}')
        button.disabled = True
        await interaction.response.edit_message(content='Actions', view=button.view)

    @discord.ui.button(label='Close', style=discord.ButtonStyle.red, custom_id='TICKET_CLOSE')
    async def delete(self, button : discord.ui.Button, interaction : discord.Interaction):
        await interaction.response.defer()
        button.disabled = True
        for num in range(1, 6).__reversed__():
            button.label = num
            await interaction.edit_original_message(content='Actions', view=button.view)
            await asyncio.sleep(1)
        
        async with self.bot.db.cursor() as cur:
            await cur.execute('DELETE FROM Tickets WHERE userID = ?', [interaction.user.id])
            await self.bot.db.commit()

        await interaction.channel.delete()
        

class Ticketing(commands.Cog):
    def __init__(self, bot : commands.Bot):
        self.bot = bot

    @commands.command()
    async def ticket(self, ctx : commands.Context):
        embed = discord.Embed(
            title="Tickets",
            description="Press the button below to open a ticket.",
            color=0x4CAF50
        )

        await ctx.send(embed=embed, view=TicketView(self.bot))

def setup(bot):
    bot.add_cog(Ticketing(bot))