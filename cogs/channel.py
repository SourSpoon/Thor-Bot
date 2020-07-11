import discord
from discord.ext import commands

from utils import checks


class Channel:
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @checks.manage_channel()
    @commands.command()
    async def block(self, ctx, *, target: discord.Member):
        """
        Blocks target from the channel, hiding it from view.

        Requires either Mod/ Admin or the name of the channel as a role. Or Manage Roles permission.
        No Custom Audit Log Entry will be created, Nor will a reason be required.
        """
        await ctx.channel.set_permissions(target, read_messages=False, reason=ctx.author)
        await ctx.send(f"{target} blocked")

    @checks.manage_channel()
    @commands.command()
    async def unblock(self, ctx, *, target: discord.Member):
        """
        Unblocks target from the channel, showing the channel again.

        Requires either Mod/ Admin or the name of the channel as a role. Or Manage Roles permission.
        No Custom Audit Log Entry will be created, Nor will a reason be required.
        """
        await ctx.channel.set_permissions(target, read_messages=None, reason=ctx.author)
        await ctx.send(f"{target} unblocked")

    @checks.manage_channel()
    @commands.command()
    async def topic(self, ctx, *, topic):
        """
        Sets topic of channel to the topic specified.

        Requires either Mod/ Admin or the name of the channel as a role. Or Manage Channels permission.
        No Custom Audit Log Entry will be created, Nor will a reason be required.
        """
        await ctx.channel.edit(topic=topic)
        await ctx.send("Topic updated!")

    @checks.manage_channel()
    @commands.command()
    async def purge(self, ctx, author: discord.Member= None):
        """
        Deletes messages from target author from the current channel.
        If no author is provided, it will delete the bot's messages.

        Requires either Mod/ Admin or the name of the channel as a role. Or Manage Channels permission.
        """
        if author is None:
            author = ctx.guild.me

        check = lambda m: m.author == author
        await ctx.channel.purge(check=check)
        await ctx.send('Purged Messages', delete_after=10)

    @commands.command()
    async def clean(self, ctx):
        """
        Deletes the bot's messages from the current channel
        No special permissions required.
        """
        check = lambda m: m.author == ctx.guild.me
        await ctx.channel.purge(check=check)
        await ctx.send('Cleaned Messages', delete_after=5)


def setup(bot):
    bot.add_cog(Channel(bot))
