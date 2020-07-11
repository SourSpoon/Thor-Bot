import datetime
import json

import aiohttp
import discord
from discord.ext import commands


class DBots:
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config['api']
        self.session = bot.session

    async def on_guild_join(self, guild):
        bot_count, memb_count = await self.guild_logger("Joined", guild)
        if (memb_count > 20) and ((bot_count / memb_count) > 0.5) and (guild.id != 110373943822540800):
            await guild.owner.send("I appear to have been added to your 'bot collection server'"
                                   " these waste my resources :( and I'll leave automatically.\n"
                                   "If you believe this has been flagged incorrectly or you require my services"
                                   " join my support server at https://discord.gg/e5XApc5")
            guild_log = self.bot.get_channel(371419385610371073)
            await guild_log.send("Triggered bot collection server")
            await guild.leave()
        else:
            self.bot.joined_guild = True

    async def on_guild_remove(self, guild):
        await self.guild_logger("Left", guild)

    async def guild_logger(self, action, guild):
        em = discord.Embed(title=f'{action} - {guild.name}')
        em.add_field(name="ID", value=guild.id)
        if action == "Joined":
            em.colour = discord.Colour.green()
            bot_count = sum(m.bot for m in guild.members)
            em.add_field(name='Approx Bot Count', value=bot_count)
        else:
            em.colour = discord.Colour.red()
        em.description = f"{guild.name}, {guild.owner}\nMember count:{guild.member_count}"
        guild_log = self.bot.get_channel(371419385610371073)
        await guild_log.send(embed=em)
        if action == "Joined":
            return bot_count, guild.member_count


def setup(bot):
    bot.add_cog(DBots(bot))
