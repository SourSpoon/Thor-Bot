import discord
from discord.ext import commands

from cogs import error
from utils import checks
from utils import embed as builder


class Member:
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.prefixes = bot.prefixes

    @commands.command()
    @checks.banner()
    async def ban(self, ctx, target: discord.Member, *, reason="None"):
        """
        Bans a target from your server, requires either the permission to ban or any role with the following names:
        Admin, Mod, Ban.

        Targets can be a mention, Name or ID.
        Your Administrator may require you to give a reason.
        If enabled a Ban entry will be created in the Audit log Channel
        """
        if (target.top_role >= ctx.author.top_role) and (ctx.guild.owner != ctx.author):
            raise error.PowerTrip
        if target.top_role >= ctx.me.top_role:
            raise error.BotPowerTrip
        settings = await self.db.fetch_settings(ctx.guild)
        if settings['log_enabled']:
            if (settings['force_reason']) and (reason == "None"):
                raise error.NoReason
            embed = builder.logger(target, "Ban", ctx.author, reason, settings['log_avatar'])
            log_channel = self.bot.get_channel(int(settings['log_channel']))
            await log_channel.send(embed=embed)
        await target.ban(reason=f'{ctx.author}({ctx.author.id}): {reason}', delete_message_days=2)
        await ctx.send(f'\N{HAMMER} {target} got banned', delete_after=120)
        await self.db.increment_ban()

    @commands.command()
    @checks.kicker()
    async def kick(self, ctx, target: discord.Member, *, reason="None"):
        """
        Kicks a target from your server, requires either the permission to kick or any role with the following names:
        Admin, Mod, Kick.

        Targets can be a mention, Name or ID.
        Your Administrator may require you to give a reason.
        If enabled a Kick entry will be created in the Audit log Channel
        """
        if (target.top_role >= ctx.author.top_role) and (ctx.guild.owner != ctx.author):
            raise error.PowerTrip
        if target.top_role >= ctx.me.top_role:
            raise error.BotPowerTrip
        settings = await self.db.fetch_settings(ctx.guild)
        if settings['log_enabled']:
            if (settings['force_reason']) and (reason == "None"):
                raise error.NoReason
            embed = builder.logger(target, "Kick", ctx.author, reason, settings['log_avatar'])
            log_channel = self.bot.get_channel(int(settings['log_channel']))
            await log_channel.send(embed=embed)
        await target.kick(reason=f'{ctx.author}({ctx.author.id}): {reason}')
        await ctx.send(f'\N{HAMMER} {target} got kicked', delete_after=120)
        await self.db.increment_kick()

    @commands.command()
    @checks.soft_ban()
    async def soft_ban(self, ctx, target: discord.Member, *, reason="None"):
        """
        Soft Bans a target from your server, a soft ban will ban someone then unban them straight away,
        this will remove all their messages from the last 48 hours
        Requires either the permission to ban or any role with the following names:
        Admin, Mod, soft.


        Targets can be a mention, Name or ID.
        Your Administrator may require you to give a reason.
        If enabled a Soft Ban entry will be created in the Audit log Channel
        """
        if (target.top_role >= ctx.author.top_role) and (ctx.guild.owner != ctx.author):
            raise error.PowerTrip
        if target.top_role >= ctx.me.top_role:
            raise error.BotPowerTrip
        settings = await self.db.fetch_settings(ctx.guild)
        if settings['log_enabled']:
            if (settings['force_reason']) and (reason == "None"):
                raise error.NoReason
            embed = builder.logger(target, "Soft Ban", ctx.author, reason, settings['log_avatar'])
            log_channel = self.bot.get_channel(int(settings['log_channel']))
            await log_channel.send(embed=embed)
        await target.ban(reason=f'{ctx.author}: {reason}', delete_message_days=2)
        await ctx.send(f'\N{HAMMER} {target} was soft banned', delete_after=120)
        await target.unban(reason="Soft Ban, see Ban entry for reason")
        await self.db.increment_soft()

    @commands.command()
    @checks.nick_names()
    async def nick(self, ctx, target: discord.Member, *, name):
        """
        Changes a  targets's Nickname on the server.

        Targets can be a mention, Name or ID.
        No reason will ever be required, nor will a custom audit log entry be generated.
        """
        if (target.top_role >= ctx.author.top_role) and (ctx.guild.owner != ctx.author):
            raise error.PowerTrip
        if target.top_role >= ctx.me.top_role:
            raise error.BotPowerTrip
        await target.edit(nick=name)
        await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')

    @commands.command()
    @checks.can_mute()
    async def mute(self, ctx, target: discord.Member, *, reason=None):
        """
        Mute's a target, stopping them from using their microphone. Will override all roles they have.

        To unmute use unmute. To check if someone is muted use check.
        Targets can be a mention, Name or ID.
        A reason is only used if your custom audit log entry is configured to allow mute entries.
        """
        if (target.top_role >= ctx.author.top_role) and (ctx.guild.owner != ctx.author):
            raise error.PowerTrip
        if target.top_role >= ctx.me.top_role:
            raise error.BotPowerTrip
        if target.voice is None:
            return await ctx.send("They need to be connected to a voice channel before I can change that!")
        await target.edit(mute=True)
        await ctx.send(f"{target} muted")
        settings = await self.db.fetch_settings(ctx.guild)
        if settings['trigger_on_mute'] and settings['log_enabled']:
            if (settings['force_reason']) and (reason is None):
                raise error.NoReason
            em = builder.logger(target, "Mute", ctx.author, reason, settings['log_avatar'])
            log = self.bot.get_channel(int(settings.log_channel))
            await log.send(embed=em)

    @commands.command()
    @checks.can_mute()
    async def unmute(self, ctx, *, target: discord.Member):
        """
        Unmute's a target, Allowing them to use their microphone. Will override any & all roles they have.

        To unmute use unmute. To check if someone is muted use check.
        Targets can be a mention, Name or ID.
        No reason will ever be required, nor will a custom audit log entry be generated.
        """
        if (target.top_role >= ctx.author.top_role) and (ctx.guild.owner != ctx.author):
            raise error.PowerTrip
        if target.top_role >= ctx.me.top_role:
            raise error.BotPowerTrip
        if target.voice is None:
            return await ctx.send("They need to be connected to a voice channel before I can change that!")
        await target.edit(mute=False)
        await ctx.send(f"{target} unmuted")

    @commands.command()
    @checks.banner()
    async def unban(self, ctx, id, *, reason="None"):
        """
        Unbans a target from your server, requires either the permission to ban or any role with the following names:
        Admin, Mod, Ban.

        Targets can only be a user ID.
        Your Administrator may require you to give a reason.
        If enabled a unban entry will be created in the Audit log Channel
        """
        target = discord.Object(id=id)
        settings = await self.db.fetch_settings(ctx.guild)
        if settings['log_enabled']:
            if (settings['force_reason']) and (reason == "None"):
                raise error.NoReason
            embed = builder.logger(target, "Unban", ctx.author, reason, settings['log_avatar'])
            log_channel = self.bot.get_channel(int(settings['log_channel']))
            await log_channel.send(embed=embed)
        await guild.unban(reason=f'{ctx.author}({ctx.author.id}): {reason}')



def setup(bot):
    bot.add_cog(Member(bot))
