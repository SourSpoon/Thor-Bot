import discord
from discord.ext import commands


from cogs import error
from utils import checks
from utils import database
from utils import embed as builder

class Test:
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db


    @commands.command(hidden=True)
    @checks.has_swag()
    async def test_ban(self, ctx):
        await self.db.increment('ban_members')
        await ctx.send("TEST!")

    @commands.command(hidden=True)
    @checks.has_swag()
    async def test_kick(self, ctx):
        await self.db.increment_kick()
        await ctx.send("TEST!")

    @commands.command(hidden=True)
    @checks.has_swag()
    async def test_soft(self, ctx):
        await self.db.increment('soft_ban')
        await ctx.send("TEST!")

def setup(bot):
    bot.add_cog(Test(bot))
