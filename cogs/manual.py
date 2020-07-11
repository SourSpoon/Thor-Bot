import asyncio

import discord
from discord.ext import commands

from cogs import error
from utils import database
from utils import embed as builder


class Manual:
    def __init__(self, bot):
        self.bot = bot
        self.db: database.SQL = bot.db

    async def on_member_ban(self, guild, user):
        await asyncio.sleep(3)
        settings = await self.db.fetch_settings(guild)
        if (not settings['trigger_on_manual']) or (not settings['log_enabled']):
            return
        if not self.perms_check(guild, settings):
            return
        async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=10):
            if entry.target.id == user.id:
                if entry.user.id == self.bot.user.id:
                    return  # make sure it's not the bot. Audit log will have been created already
                em = builder.logger(user, "Ban", entry.user, entry.reason, settings['log_avatar'])
                log_channel = self.bot.get_channel(settings['log_channel'])
                await log_channel.send(embed=em)

    async def on_member_unban(self, guild, user):
        await asyncio.sleep(3)
        settings = await self.db.fetch_settings(guild)
        if (not settings['trigger_on_manual']) or (not settings['log_enabled']):
            return
        if not self.perms_check(guild, settings):
            return
        async for entry in guild.audit_logs(action=discord.AuditLogAction.unban, limit=10):
            if entry.target.id == user.id:
                if entry.user.id == self.bot.user.id:
                    return
                em = builder.logger(user, "Unban", entry.user, entry.reason, settings['log_avatar'])
                log_channel = self.bot.get_channel(settings['log_channel'])
                await log_channel.send(embed=em)

    async def on_member_remove(self, member):
        await asyncio.sleep(3)
        settings = await self.db.fetch_settings(member.guild)
        if (not settings['trigger_on_manual']) or (not settings['log_enabled']):
            return
        if not self.perms_check(member.guild, settings):
            return
        async for entry in member.guild.audit_logs(action=discord.AuditLogAction.kick, limit=10):
            if entry.target.id == member.id:
                if entry.user.id == self.bot.user.id:
                    return
                em = builder.logger(member, "Kick", entry.user, entry.reason, settings['log_avatar'])
                log_channel = self.bot.get_channel(settings['log_channel'])
                await log_channel.send(embed=em)
        else:
            return

    async def perms_check(self, guild, settings):
        channel = self.bot.get_channel(settings.log_channel)
        if channel is None:
            raise discord.NotFound
        if not isinstance(channel, discord.TextChannel):
            raise TypeError
        channel_perms = channel.permissions_for(guild.me)

        checks = [
            not guild.me.permissions.guild_permissions.view_audit_log,
            not channel_perms.send_messages
        ]

        if not checks[0] and checks[1]:
            return await channel.send('I can\'t view the audit logs! '
                                      'This means I cant tell if someone '
                                      'left or were kicked or why someone got banned!')
        if any(checks):
            return False


def setup(bot):
    bot.add_cog(Manual(bot))
