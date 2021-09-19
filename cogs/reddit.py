import typing
import discord
from discord.ext import commands
import asyncpraw
from discord.ui import view

reddit = asyncpraw.Reddit(client_id="0w6KGyWGSfByhc3_X7OXmQ", client_secret="jIP8RPT8EXJP5_4OpDCPiBSNBwEVPw", user_agent="TBot Discord Bot asyncpraw")

class RedditView(discord.ui.View):
    def __init__(self, *, pages):
        super().__init__()
        self.pages = pages
        self.current_page = 0

    def enable_all(self):
        for child in self.children:
            child.disabled = False

    @discord.ui.button(emoji='<:left:876662119544795157>', style=discord.ButtonStyle.blurple, disabled=True)
    async def last(self, button : discord.ui.Button, interaction : discord.Interaction):
        self.current_page -= 1

        if self.current_page <= 0:
            button.disabled = True
        else:
            self.enable_all()

        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

    @discord.ui.button(emoji='<:right:876662119393816637>', style=discord.ButtonStyle.blurple)
    async def next(self, button : discord.ui.Button, interaction : discord.Interaction):
        self.current_page += 1
        if self.current_page >= len(self.pages) - 1:
            button.disabled = True
        else:
            self.enable_all()

        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

class Reddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def reddit(self, ctx : commands.Context, subreddit = 'wholesomememes'):
            subreddit = await reddit.subreddit(subreddit)
            embed = discord.Embed(description='Loading...', color=discord.Color.blurple())
            msg = await ctx.send(embed=embed)
            await subreddit.load()

            if subreddit.over18:
                embed.description = "Can't get Reddit feed from an NSFW subreddit."
                await msg.edit(embed=embed)
                return
            
            submissionEmbeds = []
            async for submission in subreddit.hot(limit=10):
                embed = discord.Embed(url='https://www.reddit.com' + submission.permalink)
                embed.title = submission.title
                embed.description = f'[u/{submission.author}](https://www.reddit.com/u/{submission.author.name})'
                embed.color = discord.Color.blurple()
                embed.set_image(url=submission.url)
                submissionEmbeds.append(embed)

            view = RedditView(pages=submissionEmbeds)
            await msg.edit(embed=submissionEmbeds[0], view=view)


def setup(bot):
    bot.add_cog(Reddit(bot))