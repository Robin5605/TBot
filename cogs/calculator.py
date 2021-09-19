import discord
from discord.ext import commands
import typing

class CalcView(discord.ui.View):
    def __init__(self, *, caller : discord.Member):
        super().__init__()
        self.caller = caller
        self.input = ''
        self.add_buttons()
    
    def add_items(self, *items : typing.List[discord.ui.Item]) -> None:
        """ Custom implementation of `add_item` to support passing in a list, or multiple lists"""
        for item in items:
            for subitem in item:
                super().add_item(subitem)

    async def interaction_check(self, interaction: discord.Interaction):
        if not interaction.user == self.caller:
            await interaction.response.send_message(content='You cannot use that.', ephemeral=True)
            return False
        return True

    def add_buttons(self):
        self.number_buttons = []
        row = 0
        for num in range(1, 10):
            # Use a loop to add 1-9 since doing it manually is un-DRY
            self.number_buttons.append(CalcButton(label=num, style=discord.ButtonStyle.gray, row=row))
            if num % 3 == 0:
                row += 1

        self.bottom_row = [
            CalcButton(label=0, style=discord.ButtonStyle.gray, row=3),
            CalcButton(label='.', style=discord.ButtonStyle.gray, row=3),
            CalcButton(label='=', style=discord.ButtonStyle.green, row=3),
        ]
        self.operators = [
            CalcButton(label='/', style=discord.ButtonStyle.blurple, row=0, disabled=True),
            CalcButton(label='*', style=discord.ButtonStyle.blurple, row=1, disabled=True),
            CalcButton(label='-', style=discord.ButtonStyle.blurple, row=2, disabled=True),
            CalcButton(label='+', style=discord.ButtonStyle.blurple, row=3, disabled=True),
        ]
        self.options = [
            CalcButton(label='Del', style=discord.ButtonStyle.red, row=0),
            CalcButton(label='Clear', style=discord.ButtonStyle.red, row=1),
            CalcButton(label='Quit', style=discord.ButtonStyle.red, row=2),
        ]

        self.add_items(self.number_buttons, self.bottom_row, self.operators, self.options)

class CalcButton(discord.ui.Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def callback(self, interaction: discord.Interaction):
        if self.label == '=':
            try:
                self.view.input = str(eval(self.view.input))
                await interaction.response.edit_message(content=self.view.input)
            except:
                await interaction.response.edit_message(content='ERROR')
            
            return

        if self.label == 'Delete':
            self.view.input = self.view.input[0:-1]
        elif self.label == 'Clear':
            self.view.input == ''
        elif self.label == 'Quit':
            await interaction.message.delete()
            return

        new_content = self.update_display()
        new_view = self.update_view()
        await interaction.response.edit_message(content=new_content, view=new_view)
        

    def update_display(self) -> str:
        if not self in self.view.options:
            self.view.input += str(self.label)
        escaped = discord.utils.escape_markdown(self.view.input)
        return escaped

    def update_view(self) -> discord.ui.View:
        view = self.view
        input : str = view.input
        lastNum = int(input) if input.isdigit() else None

        ops = ['/', '*', '-', '+']
        if lastNum:
            for child in view.children:
                child.disabled = False
        else:
            for child in view.children:
                if child.label in ops:
                    child.disabled = True
        
        return view

class Calculator(commands.Cog):
    def __init__(self, bot : commands.Bot):
        self.bot = bot

    @commands.command(aliases=['calc'])
    async def calculator(self, ctx : commands.Context):
        view = CalcView(caller=ctx.author)
        await ctx.send("0", view=view)

def setup(bot):
    bot.add_cog(Calculator(bot))