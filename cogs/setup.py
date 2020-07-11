import datetime

import discord
from discord.ext import commands


from utils import checks
from utils import database
from utils.database import SQL

true_list = ['t', '1', 'true', 'y', 'yes']
false_list = ['f', '0', 'false', 'n', 'no']
role_description = "Any roles that have been created have been placed at the bottom of the hierarchy, " \
                   "please ensure they are placed correctly so that those with Manage_Roles permissions " \
                   "can not assign roles they shouldn't"

settings_msg = """
```
Audit Log Enabled: {}
Audit Log Channel: {}
Post Log On Mute: {}
Post Log On Manual: {}
Post Avatar in Log: {}
Force Reason on Ban/ Kick: {}
```
"""

class Setup:
    def __init__(self, bot):
        self.bot = bot
        self.db: SQL = bot.db
        self.prefixes = bot.prefixes

    @commands.group(has_subcommands=True, invoke_without_command=True)
    @commands.guild_only()
    async def settings(self, ctx):
        """
        Lists your current thor bot settings. Has sub-commands.

        Can not be used in DMs
        """
        settings = dict(await self.db.fetch_settings(ctx.guild))
        if settings['log_channel'] is not None:
            audit_channel = self.bot.get_channel(settings['log_channel'])
            if audit_channel is None:
                audit_channel = "Channel not found"
            else:
                audit_channel = audit_channel.name
        else:
            audit_channel = "No Channel Set"

        em = discord.Embed(
            title=f'Settings for {ctx.guild.name}',
            colour=0x36393E,
            description=settings_msg.format(
                settings['log_enabled'],
                audit_channel, settings['trigger_on_mute'],
                settings['trigger_on_manual'],
                settings['log_avatar'],
                settings['force_reason']
            )
        )

        await ctx.send(embed=em)

    @settings.command()
    @checks.has_admin()
    async def audit_log(self, ctx, channel: discord.TextChannel=None):
        """
        Sets an Audit Log channel and enables the audit log

        If no channel is specified it will turn the Audit logs off
        Requires Manage Server permission or Admin role.
        """
        if channel is not None:
            db_channel = channel.id
        else:
            db_channel = None
        await self.db.audit_log(ctx, db_channel)
        await ctx.send(f"Audit Channel set to {channel}")

    @settings.command()
    @checks.has_admin()
    async def force_reasons(self, ctx):
        """
        Toggles forces Kicks, Bans and Softbans to have a reason.

        Requires Manage Server permission or Admin role.
        """
        req_reason = await self.db.toggle_force_reason(ctx.guild)
        if req_reason:
            await ctx.send('Force Reason Is currently enabled')
        else:
            await ctx.send('Force Reason is currently disabled')

    @commands.command()
    @checks.has_admin()
    async def log_avatar(self, ctx, *, setting="None"):
        """
        Toggles posting target's avatar in the custom audit log.

        Available settings: "True" or "False", default value: True
        If the reason in any kick, ban, mute ect has "NSFW" in it's text
        it will not post the avatar no matter the setting.

        Requires Manage Server permission or Admin role.
        """
        if setting.lower() in true_list:
            await self.db.audit_log(ctx, True)
            await ctx.send("Future posts will include target's avatar")
        elif setting.lower() in false_list:
            await self.db.audit_log(ctx, False)
            await ctx.send("Future posts will no longer include target's avatar")
        else:
            await ctx.invoke(self.bot.get_command("help"), "force_reasons")
            settings = await self.db.fetch_settings(ctx.guild)
            await ctx.send(f"Current setting: {settings['log_avatar']}")

    @settings.command()
    @checks.has_admin()
    async def delete_all_settings(self, ctx):
        """
        Deletes all settings for your server, including prefix. Irreversible.

        Requires Manage Server permission or Admin role.
        """
        await self.db.delete_settings(ctx)
        self.prefixes.pop(ctx.guild.id, None)
        await ctx.send("settings deleted")

    @settings.command()
    @checks.has_admin()
    async def reset_to_default(self, ctx):
        """
        Restores all data to their default value including prefix. Irreversible.

        Requires Manage Server or Admin role.
        """
        await self.db.delete_settings(ctx)
        self.prefixes.pop(ctx.guild.id, None)
        await self.db.new_record(ctx.guild)
        await ctx.send("Settings returned to default values.")

    @settings.command()
    @checks.has_admin()
    async def audit_log_manual(self, ctx):
        """
        Toggles audit log entries for bans, kicks and unbans with another bot or through the discord client.
        You will need to enable and set an audit log channel separately.

        Requires Manage Server permission or Admin role.
        """
        enabled = await self.db.toggle_manual_log(ctx.guild)
        if enabled:
            await ctx.send("Audit log tracking for manual bans is now enabled")
        else:
            await ctx.send("Audit log tracking for manual bans is now disabled")

    @commands.command()
    @checks.has_admin()
    async def setup_roles(self, ctx, option="h"):
        """
        Creates Roles to use bot.  Roles are created at the bottom of the role hierarchy
        and may need to be reordered.

        Requires Manage Server permission or Admin role.

        Available options:
        h: Shows this message (default)
        f: Fast, creates 2 roles, Admin and Mod. Mod can do all moderation commands (like Kick, Ban ect)
                but not change bot settings. Admin can do all commands
        v: Verbose, creates a role for each moderation action, and an Admin role to change bot settings
        """
        option = option.lower()
        if option == "f":
            await self._setup_roles_fast(ctx)
        elif option == "h":
            await ctx.invoke(self.bot.get_command("help"), "setup roles")
        elif option == "v":
            await self._setup_roles_verbose(ctx)

    async def _setup_roles_fast(self, ctx):
        em = discord.Embed(title="Roles", description=role_description)
        for role in ctx.guild.roles:
            if (role.name.lower() == "admin") or (role.name.lower() == "swagmin"):
                em.add_field(name="", value="Admin / Swagmin role already exists")
                break
        else:
            await ctx.guild.create_role(name="Admin", reason="Admin Role to use Thor Bot")

        for role in ctx.guild.roles:
            if role.name.lower() == "mod":
                em.add_field(name="", value="Mod Role already exists")
                break
        else:
            await ctx.guild.create_role(name="Mod", reason="Mod Role to use Thor Bot")
        await ctx.send(embed=em)

    async def _setup_roles_verbose(self, ctx):
        em = discord.Embed(title="Roles", description=role_description)
        for role in ctx.guild.roles:
            if (role.name.lower() == "admin") or (role.name.lower() == "swagmin"):
                em.add_field(name="", value="Admin / Swagmin role already exists")
                break
        else:
            await ctx.guild.create_role(name="Admin", reason="Admin Role to use Thor Bot")

        for role in ctx.guild.roles:
            if role.name.lower() == "kick":
                em.add_field(name="", value="Kick Role already exists")
                break
        else:
            await ctx.guild.create_role(name="Kick", reason="Kick Role to use Thor Bot")

        for role in ctx.guild.roles:
            if role.name.lower() == "ban":
                em.add_field(name="", value="Ban Role already exists")
                break
        else:
            await ctx.guild.create_role(name="Ban", reason="Ban Role to use Thor Bot")

        for role in ctx.guild.roles:
            if role.name.lower() == "manage nick":
                em.add_field(name="", value="Manage Nick Role already exists")
                break
        else:
            await ctx.guild.create_role(name="Manage Nick", reason="Manage Nickname Role to use Thor Bot")

        for role in ctx.guild.roles:
            if role.name.lower() == "soft":
                em.add_field(name="", value="Soft Role already exists")
                break
        else:
            await ctx.guild.create_role(name="Soft", reason="Soft Ban Role to use Thor Bot")

        for role in ctx.guild.roles:
            if role.name.lower() == "manage channel":
                em.add_field(name="", value="Manage Channel role already exists")
                break
        else:
            await ctx.guild.create_role(name="Manage Channel", reason="Manage Channel Role to use Thor Bot")

        await ctx.send(embed=em)

    @commands.command()
    @checks.banner()
    async def remove_img(self, ctx, message_id: int):
        """
        Used to remove an Image from the mod log. Useful if you forgot to add 'nsfw' to a reason,
        or otherwise need to remove an image. Must be used in the same server as the mod-log.

        message_id must be the ID of a moderation log entry sent by Thor Bot.

        Requires either the permission to ban or any role with the following names:
        Admin, Mod, Ban.
        """
        settings = await self.db.fetch_settings(ctx.guild)
        mod_log = discord.utils.find(lambda c: c.id == settings.get('log_channel', None), ctx.guild.channels)
        if mod_log is None:
            return await ctx.send('Mod-log channel not found')
        try:
            entry: discord.Message = await mod_log.get_message(message_id)
        except discord.NotFound:
            return await ctx.send('Message Not Found')
        except discord.Forbidden:
            return await ctx.send('I don\'t have permissions for that!')
        except discord.HTTPException:
            return await ctx.send('Retrieving the message failed')
        if any([entry.author.id != self.bot.user.id, len(entry.embeds) == 1]):
            return await ctx.send('That doesn\'t look like a valid mod-log entry')
        embed: discord.Embed = entry.embeds[0]
        embed._thumbnail = dict()
        await entry.edit(embed=embed)
        await ctx.message.add_reaction('\N{OK HAND SIGN}')


def setup(bot):
    bot.add_cog(Setup(bot))
