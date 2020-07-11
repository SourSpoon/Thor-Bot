import datetime
import json

import discord
from discord.ext import commands

from utils import checks


class General:
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        print('Logged In As')
        print(self.bot.user.name)
        print(self.bot.user.id)
        print(discord.__version__)
        print('---------')

    @checks.has_swag()
    @commands.command(name='load', hidden=True)
    async def _load(self, ctx, *, cog: str):
        """Loads a module."""

        cog = f'cogs.{cog.lower()}'
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send('\N{PISTOL}')
            await ctx.send(f'{type(e).__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @checks.has_swag()
    @commands.command(name='reload', hidden=True)
    async def _reload(self, ctx, *, cog: str):
        """Reloads a module."""

        cog = f'cogs.{cog.lower()}'
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send('\N{PISTOL}')
            await ctx.send(f'{type(e).__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @checks.has_swag()
    @commands.command(name='unload', hidden=True)
    async def _unload(self, ctx, *, cog: str):
        """Unloads a module."""

        cog = f'cogs.{cog.lower()}'
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send('\N{PISTOL}')
            await ctx.send(f'{type(e).__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')


def setup(bot):
    bot.add_cog(General(bot))
