import json

import discord
from discord.ext import commands

from cogs import error


kick = ('admin', 'Admin', 'Mod', 'mod', 'Kick', 'kick', 'Swagmin', 'swagmin')
nick = ('admin', 'Admin', 'Mod', 'mod', 'Manage Nick', 'manage nick', 'Swagmin', 'swagmin')
ban = ('admin', 'Admin', 'Mod', 'mod', 'ban', 'Ban', 'Swagmin', 'swagmin')
soft = ('admin', 'Admin', 'Mod', 'mod', 'soft', 'soft', 'Swagmin', 'swagmin')
topic = ('admin', 'Admin', 'Mod', 'mod', 'Manage Channel', 'manage channel', 'Swagmin', 'swagmin')
mute = ('admin', 'Admin', 'Mod', 'mod', 'Swagmin', 'swagmin', 'mute', 'Mute')
silence = ('admin', 'Admin', 'Mod', 'mod', 'Swagmin', 'swagmin', 'silence', 'Silence')
admin = ('admin', 'Admin', 'Swagmin', 'swagmin')

def load_swag():
    with open('data/swag.json', 'r') as doc:
        return json.load(doc)


def has_swag():
    def predicate(ctx):
        swag = load_swag()
        if ctx.author.id in swag:
            return True
    return commands.check(predicate)


def kicker():
    def predicate(ctx):
        if not isinstance(ctx.channel, discord.abc.GuildChannel):
            return False
        if not ctx.guild.me.guild_permissions.kick_members:
            raise error.BotPermissions
        if ctx.author.guild_permissions.kick_members:
            return True
        check = lambda r: r.name in kick
        role = discord.utils.find(check, ctx.author.roles)
        return role
    return commands.check(predicate)


def banner():
    def predicate(ctx):
        if not isinstance(ctx.channel, discord.abc.GuildChannel):
            raise error.AuditEntryMissing
        if not ctx.guild.me.guild_permissions.ban_members:
            raise error.BotPermissions
        if ctx.author.guild_permissions.ban_members:
            return True
        check = lambda r: r.name in ban
        role = discord.utils.find(check, ctx.author.roles)
        return role
    return commands.check(predicate)


def nick_names():
    def predicate(ctx):
        if not isinstance(ctx.channel, discord.abc.GuildChannel):
            return False
        if not ctx.guild.me.guild_permissions.manage_nicknames:
            raise error.BotPermissions
        if ctx.author.guild_permissions.manage_nicknames:
            return True
        check = lambda r: r.name in nick
        role = discord.utils.find(check, ctx.author.roles)
        return role
    return commands.check(predicate)


def manage_channel():
    def predicate(ctx):
        if not isinstance(ctx.channel, discord.abc.GuildChannel):
            return False
        if not ctx.guild.me.guild_permissions.manage_channels:
            raise error.BotPermissions
        if ctx.author.guild_permissions.manage_channels:
            return True
        check = lambda r: (r.name in topic) or (r.name.lower() == ctx.channel.name.lower())
        role = discord.utils.find(check, ctx.author.roles)
        return role
    return commands.check(predicate)


def soft_ban():
    def predicate(ctx):
        if not isinstance(ctx.channel, discord.abc.GuildChannel):
            return False
        if not ctx.guild.me.guild_permissions.ban_members:
            raise error.BotPermissions
        if ctx.author.guild_permissions.ban_members:
            return True
        check = lambda r: r.name in soft
        role = discord.utils.find(check, ctx.author.roles)
        return role
    return commands.check(predicate)


def has_admin():
    def predicate(ctx):
        if not isinstance(ctx.channel, discord.abc.GuildChannel):
            return False
        if ctx.author.guild_permissions.manage_guild:
            return True
        check = lambda r: r.name in admin
        role = discord.utils.find(check, ctx.author.roles)
        return role
    return commands.check(predicate)


def can_mute():
    def predicate(ctx):
        if not isinstance(ctx.channel, discord.abc.GuildChannel):
            return False
        if not ctx.guild.me.guild_permissions.manage_roles:
            raise error.BotPermissions
        if ctx.author.guild_permissions.manage_roles:
            return True
        check = lambda r: r.name in mute
        role = discord.utils.find(check, ctx.author.roles)
        return role
    return commands.check(predicate)


def can_silence():
    def predicate(ctx):
        if not isinstance(ctx.channel, discord.abc.GuildChannel):
            return False
        if not ctx.guild.me.guild_permissions.manage_roles:
            raise error.BotPermissions
        if ctx.author.guild_permissions.manage_roles:
            return True
        check = lambda r: r.name in silence
        role = discord.utils.find(check, ctx.author.roles)
        return role
    return commands.check(predicate)
