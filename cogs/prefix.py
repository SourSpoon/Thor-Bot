import discord
from discord.ext import commands

from utils import checks


class Prefix:
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.prefixes = bot.prefixes

    @commands.group(name="prefix", invoke_without_command=True, has_subcommands=True)
    async def _prefix(self, ctx):
        """
        Manages your servers prefixes. Has sub-commands.

        Default Prefix is: ?
        You will always be able to mention the bot if you don't have one.
        """
        if self.prefixes.get(ctx.guild.id, None) is None:
            await ctx.send('You have no prefixes set! You can always mention the bot though')
        else:
            pretty = str(self.prefixes[ctx.guild.id])
            await ctx.send(f"Prefixes: `{pretty[1:-1]}`\nYou can also mention the bot")

    @_prefix.command()
    @checks.has_admin()
    async def add(self, ctx, *, prefix):
        """
        Adds a prefix, almost any prefix can be specified.

        Prefixes ending with a space will not work as intended. (discord limitation)
        """
        try:
            self.prefixes[ctx.guild.id].append(prefix)
            self.prefixes[ctx.guild.id] = list(set(self.prefixes[ctx.guild.id]))
            self.prefixes[ctx.guild.id].sort(key=len, reverse=True)
        except AttributeError:
            self.prefixes[ctx.guild.id] = [prefix]
        except KeyError:
            self.prefixes[ctx.guild.id] = [prefix]
        await self.db.update_prefix(ctx.guild, self.prefixes[ctx.guild.id])
        await ctx.send(f'Added prefix `{prefix}`')

    @_prefix.command(aliases=['del', 'delete', 'rem'])
    @checks.has_admin()
    async def remove(self, ctx, *, prefix):
        """
        Removes an existing prefix
        """
        if prefix in self.prefixes[ctx.guild.id]:
            self.prefixes[ctx.guild.id].remove(prefix)
            await self.db.update_prefix(ctx.guild, self.prefixes[ctx.guild.id])
            return await ctx.send(f"`{prefix}` removed")
        else:
            await ctx.send(f"prefix `{prefix}` not found")

    @_prefix.command(hidden=True)
    @checks.has_swag()
    async def clear(self, ctx):
        """
        Clears All prefixes, Special powers only.
        """
        self.prefixes[ctx.guild.id] = None
        await self.db.update_prefix(ctx.guild, None)
        await ctx.send("Cleared all Prefixes")

    @_prefix.command(hidden=True)
    @checks.has_swag()
    async def force_clear(self, ctx, guild_id: int):
        self.prefixes[ctx.guild.id] = None
        await self.db.update_prefix_(guild_id, None)
        self.bot.prefixes.pop(guild_id, None)
        await ctx.send("Forced prefix clear")

    @_prefix.command()
    async def list(self, ctx):
        """
        Lists all prefixes configured for the current server.
        """
        if self.prefixes.get(ctx.guild.id, None) is None:
            await ctx.send('You have no prefixes set! You can always mention the bot though')
        else:
            pretty = str(self.prefixes[ctx.guild.id])
            await ctx.send(f"Prefixes: `{pretty[1:-1]}`\nYou can also mention the bot")

def setup(bot):
    bot.add_cog(Prefix(bot))
