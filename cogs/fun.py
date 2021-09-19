import discord
from discord.ext import commands

class TTTVButton(discord.ui.Button):
    def __init__(self, x : int, y : int):
        super().__init__(style=discord.ButtonStyle.gray, label='\u200b', row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        view : TTTView = self.view
        state = view.board[self.y][self.x]
        
        if state in (view.X, view.O):
            return

        if view.current_player == view.X:
            self.style = discord.ButtonStyle.danger
            self.label = 'X'
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = "It is now O's turn"
        else:
            self.style = discord.ButtonStyle.success
            self.label = 'O'
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = "It is now X's turn"

        winner = view.check_winner()
        if winner is not None:
            if winner == view.X:
                content = 'X won!'
            elif winner == view.O:
                content = 'O won!'
            else:
                content = "It's a tie!"

            for child in view.children:
                child.disabled = True

            view.stop()


        await interaction.response.edit_message(content=content, view=view)

class TTTView(discord.ui.View):

    X = -1
    O = 1

    def __init__(self, player1 : discord.Member, player2 : discord.Member):
        super().__init__()
        self.player1 = player1
        self.player2 = player2
        self.current_player = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        for x in range(3):
            for y in range(3):
                self.add_item(TTTVButton(x, y))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.current_player == self.X and interaction.user != self.player1:
            await interaction.response.send_message(f'It is {self.player2.mention}\'s turn right now!')
            return False
        elif self.current_player == self.O and interaction.user != self.player2:
            await interaction.response.send_message(f'It is {self.player1.mention}\'s turn right now!')
            return False

        return True

    def check_winner(self):
        for horizontal in self.board:
            value = sum(horizontal)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None

class RPSButton(discord.ui.Button):
    def __init__(self, *, emoji):
        super().__init__(emoji=emoji)

    async def callback(self, interaction: discord.Interaction):
        view : RPSView = self.view 

        if interaction.user not in view.choices:
            await interaction.response.send_message('This game is not for you.')
            return

        if interaction.user == view.player1:
            view.choice1 = view.emojis.index(self.label)
        elif interaction.user == view.player2:
            view.choice2 = view.emojis.index(self.label)

        if view.choice1 and view.choice2:
            winner = view.check_winner()
            await interaction.response.send_message(f'{winner.mention} was the winner!')
            return

class RPSView(discord.ui.View):

    emojis = ['💎', '📝', '✂️']

    def __init__(self, player1 : discord.Member, player2 : discord.Member):
        super().__init__()
        self.player1 = player1
        self.choice1 = None
        self.player2 = player2
        self.choice2 = None
        for emoji in self.emojis:
            self.add_item(RPSButton(emoji=emoji))

    def check_winner(self) -> discord.Member:
        if self.choice1 == 0 and self.choice2 == 2:
            return self.player1
        elif self.choice1 == 2 and self.choice2 == 0:
            return self.player2
        elif self.choice1 > self.choice2:
            return self.player1
        elif self.choice1 < self.choice2:
            return self.player2

        return None


class Fun(commands.Cog):
    def __init__(self, bot : commands.Bot):
        self.bot = bot

    @commands.command()
    async def ttt(self, ctx : commands.Context, member : discord.Member):
        view = TTTView()
        await ctx.send('Tic Tac Toe', view=view)

    @commands.command()
    async def rps(self, ctx : commands.Context, member : discord.Member):
        view = RPSView()
        await ctx.send(f'Rock Paper Scissors: {ctx.author.mention} vs {member.mention}',view=view)

def setup(bot):
    bot.add_cog(Fun(bot))