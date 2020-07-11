import asyncio
import datetime
import json
import logging
from pathlib import Path

import asyncpg
import aiohttp
import discord
from discord.ext import commands

from utils.database import SQL
from utils import time

description = """
Thor bot is a moderation bot with a granular permissions system. Still in development, so be gentle!
The help command will only show commands that can run,
so if the bot or you don't have the correct permissions they will not show!
"""

def config_load():
    with open('data/config.json', 'r') as doc:
        dump = json.load(doc)
        return dump


async def run():
    config = config_load()
    pool = await asyncpg.create_pool(**config['pg'])
    db = SQL(pool)

    bot = Bot(db=db, config=config, description=description)

    token = config['token']
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        await bot.shut_me_down_daddy()
    except Exception as e:
        error = f'{type(e).__name__}: {e}'
        print(f"Bot Dun Goofed\n{error}")
    finally:
        bot.loop.close()


class Context(commands.Context):
    @property
    def session(self):
        return self.bot.session


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        self.db: SQL = kwargs.pop('db')
        self.config = kwargs.pop('config')
        self.api_keys = self.config['api']
        self.prefixes = {}
        self.joined_guild = False
        super().__init__(
            command_prefix=self._get_prefix,
            fetch_offline_members=False,
            description=kwargs.pop('description')
        )
        self.loop.create_task(self.track_uptime())
        self.loop.create_task(self.stats_poster())
        self.loop.create_task(self.load_all_extensions())
        self.session = aiohttp.ClientSession(loop=self.loop)

    async def track_uptime(self):
        await self.wait_until_ready()
        self.start_time = datetime.datetime.utcnow()

    async def load_prefixes(self, guild):
        prefix = await self.db.fetch_prefix(guild)
        if prefix is not None:
            prefix.sort(key=len, reverse=True)
            self.prefixes[guild.id] = prefix
        return prefix

    async def _get_prefix(self, bot, message):
        if message.guild is None:
            prefix = ["?"]
            return commands.when_mentioned_or(*prefix)(bot, message)
        try:
            prefix = self.prefixes[message.guild.id]
        except KeyError:
            prefix = await self.load_prefixes(message.guild)
        if prefix is None:
            return commands.when_mentioned(bot, message)
        else:
            return commands.when_mentioned_or(*prefix)(bot, message)

    @property
    def uptime(self):
        delta = datetime.datetime.utcnow() - self.start_time
        if delta.total_seconds() >= 3600:
            mod = delta.total_seconds() % 3600
            simp_time = delta.total_seconds() - mod
            return time.human_time(simp_time)
        return time.human_time(delta.total_seconds())

    async def on_message(self, message):
        if message.author.bot:
            return
        ctx = await self.get_context(message, cls=Context)
        if ctx.prefix is not None:
            ctx.command = self.all_commands.get(ctx.invoked_with.lower())
            await self.invoke(ctx)

    async def on_ready(self):
        print('-'*10)
        self.appinfo = await self.application_info()
        print(f"Logged in as: {self.user.name}\nwith discord version: {discord.__version__}\n"
              f"Owner: {self.appinfo.owner}")
        print("-"*10)

    async def load_all_extensions(self):
        await self.wait_until_ready()
        await asyncio.sleep(1)
        startup_extensions = [x.stem for x in Path('cogs').glob('*.py')]
        for extension in startup_extensions:
            try:
                self.load_extension(f'cogs.{extension}')
                print(f'loaded {extension}')
            except Exception as e:
                error = f'{extension}\n {type(e).__name__}: {e}'
                print(f'Failed to load extension {error}')
        print("-" * 10)


    async def download_cache(self):
        small_guilds = []
        await self.wait_until_ready()
        for guild in self.guilds:
            if (not guild.unavailable) and (guild.member_count < 10_000) and guild.large:
                small_guilds.append(guild)
        await self.request_offline_members(*small_guilds)

    async def on_guild_join(self, guild):
        await self.db.new_record(guild)
        if (guild.member_count < 10_100) and guild.large:
            await self.request_offline_members(guild)

    async def stats_poster(self):
        while True:
            await self.wait_until_ready()
            await asyncio.sleep(1800)
            if self.joined_guild:
                await self.discord_bots_list()
                await self.dbots_pw()
                self.joined_guild = False

    async def discord_bots_list(self):
        headers = {
            'Authorization': self.api_keys['dbl'],
            'Content-Type': 'application/json'
        }
        data = {'server_count': len(self.guilds)}
        info = self.appinfo
        req = await self.session.post(f'https://discordbots.org/api/bots/{info.id}/stats',
                                      data=json.dumps(data), headers=headers)
        if req.status == 200:
            return
        else:
            resp = await req.text()
            em = discord.Embed(title='dbl Update failed', colour=discord.Colour.red())
            em.set_footer(text='Occurred On')
            em.timestamp = datetime.datetime.utcnow()
            em.description = f'```status: {req.status}\n\n {resp}```'
            error_log = self.get_channel(356967454443962375)
            await error_log.send(embed=em)

    async def dbots_pw(self):
        headers = {
            'Authorization': self.api_keys['dbots'],
            'Content-Type': 'application/json'
        }
        data = {'server_count': len(self.guilds)}
        req = await self.session.post(f'https://bots.discord.pw/api/bots/{self.user.id}/stats',
                                      data=json.dumps(data), headers=headers)

        if req.status == 200:
            return
        else:
            resp = await req.text()
            em = discord.Embed(title='d bots Update failed', colour=discord.Colour.red())
            em.set_footer(text='Occurred On')
            em.timestamp = datetime.datetime.utcnow()
            em.description = f'```status: {req.status}\n\n {resp}```'
            error_log = self.get_channel(356967454443962375)
            await error_log.send(embed=em)

    async def shut_me_down_daddy(self):
        await self.db.db.close()
        await self.session.close()
        for cog in self.cogs:
            self.unload_extension(cog)
        await self.logout()


if __name__ == '__main__':
    # set up logging
    logger = logging.getLogger('discord')
    logger.setLevel(logging.WARNING)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())


