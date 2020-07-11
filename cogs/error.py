import datetime
import traceback

import discord
from discord.ext import commands

class BotPowerTrip(commands.CommandError):
    def __init__(self):
        msg = 'The bot has a lower top most role than the target.'
        super().__init__(msg)

class BotPermissions(commands.CommandError):
    def __init__(self):
        msg = 'The bot does not have permissions necessary to perform that action.'
        super().__init__(msg)


class NoReason(commands.CommandError):
    def __init__(self):
        msg = 'Your administrator has required you to enter a reason'
        super().__init__(msg)


class PowerTrip(commands.CommandError):
    def __init__(self):
        msg = f'You are unable to moderate that target'
        super().__init__(msg)


class AuditEntryMissing(commands.CommandError):
    def __init__(self):
        msg = "audit log entry not found"
        super().__init__(msg)

class Error:
    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, error):

        if hasattr(ctx.command, 'on_error'):
            return

        cog = ctx.cog
        if cog:
            attr = f'_{cog.__class__.__name__}__error'
            if hasattr(cog, attr):
                return

        error = getattr(error, 'original', error)

        ignored = (commands.CommandNotFound, commands.UserInputError,
                   commands.MissingPermissions, commands.CheckFailure)

        if isinstance(error, ignored):
            return

        handler = {
            discord.Forbidden: '**I do not have the required permissions to run this command.**',
            commands.DisabledCommand: f'{ctx.command} has been disabled.',
            commands.NoPrivateMessage: f'{ctx.command} can not be used in Private Messages.',
            commands.CheckFailure: '**You aren\'t allowed to use this command!**',
            NoReason: 'Your administrator has required you to enter a reason',
            PowerTrip: f'You can not invoke {ctx.command} on someone with the same or higher role than yourself',
            BotPermissions: f"The bot can not invoke {ctx.command} as it doesn't have permissions to do so",
            BotPowerTrip: f"The bot can not invoke {ctx.command} on that target,"
                          f" It needs to have a higher top-most role!"

        }

        try:
            message = handler[type(error)]
        except KeyError:
            pass
        else:
            return await ctx.send(message)

        embed = discord.Embed(title=f'Command Exception', color=discord.Color.red())
        embed.set_footer(text='Occured on')
        embed.timestamp = datetime.datetime.utcnow()

        exc = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=False))
        exc = exc.replace('`', '\u200b`')
        embed.description = f'```py\n{exc}\n```'

        embed.add_field(name='Command', value=ctx.command.qualified_name)
        embed.add_field(name='Invoker', value=ctx.author)
        embed.add_field(name='Location', value=f'Guild: {ctx.guild}\nChannel: {ctx.channel}')
        embed.add_field(name='Message', value=ctx.message.content)

        await ctx.bot.get_channel(356967454443962375).send(embed=embed)




def setup(bot):
    bot.add_cog(Error(bot))
