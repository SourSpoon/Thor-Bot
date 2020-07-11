from contextlib import redirect_stdout
import json
import io
import textwrap
import traceback

import discord
from discord.ext import commands

from utils import checks
from utils import database


class Swag:
    def __init__(self, bot):
        self.bot = bot
        self.db: database.SQL = bot.db

    def cleanup_code(self, content):
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])
        return content.strip('` \n')

    def get_syntax_error(self, e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

    @checks.has_swag()
    @commands.command(name='eval', hidden=True)
    async def _eval(self, ctx, *, body: str):
        """Evaluates code."""
        env = {
            'bot': ctx.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            'sql': ctx.bot.db.db
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        code = textwrap.indent(body, '  ')
        to_compile = f'async def func():\n{code}'

        try:
            exec(to_compile, env)
        except SyntaxError as e:
            return await ctx.send(self.get_syntax_error(e))

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\N{HAMMER}')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                ctx.bot._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    @commands.command(hidden=True)
    async def update_swag(self, ctx):
        swag_members = []
        swag_guild = self.bot.get_guild(353532692005912587)
        swag_role = discord.utils.get(swag_guild.roles, id=353532767432081412)
        for member in swag_role.members:
            swag_members.append(member.id)
        with open('data/swag.json', 'w') as doc:
            json.dump(swag_members, doc)

    @commands.command(hidden=True)
    @checks.has_swag()
    async def guild_reset(self, ctx, id, prefix=None):
        if prefix is None:
            await self.db.reset_guild(int(id))
        else:
            prefix_list =[]
            prefix_list.append(prefix)
            await self.db.reset_guild(int(id), prefix_list)
        await ctx.send(f'Guild {id} reset')


def setup(bot):
    bot.add_cog(Swag(bot))
