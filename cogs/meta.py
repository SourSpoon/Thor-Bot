import discord
from discord.ext import commands
import psutil


class Meta:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def hello(self, ctx):
        """
        Basic command, normally used to test if the bot is online.
        """
        await ctx.send('Hello! I am a discord bot written by Spoon#7805')

    @commands.command(name="info", aliases=['about'])
    async def _info(self, ctx):
        """Posts info about the bot"""
        em = discord.Embed(
            title="Thor Bot",
            description="A moderation bot written by Spoon#7805 currently in testing phases.\n"
                        "If you can please provide feedback at my support server",
            color=discord.Colour(0x00FFF0),
            url='https://github.com/SourSpoon/Thor-Bot/blob/master/readme.md'
        )
        em.add_field(name='Serving', value=f"{str(len(self.bot.guilds))} guilds\n"
                                           f"{sum (len(g.channels) for g in self.bot.guilds)} channels\n"
                                           f"{sum(g.member_count for g in self.bot.guilds)} users\n")
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent()
        em.add_field(name='Performance', value=f'ping: {int(self.bot.latency*1000)}ms\n'
                                               f'RAM: {mem.percent}%\n'
                                               f'CPU: {cpu}%')
        em.add_field(name='Links', value='[Support Server](https://discord.gg/e5XApc5)\n'
                                         '[Read Me](https://github.com/SourSpoon/Thor-Bot/blob/master/readme.md)\n'
                                         '[Project Roadmap](https://github.com/SourSpoon/Thor-Bot/projects/1)')
        em.add_field(name="Uptime", value=self.bot.uptime)
        em.set_footer(text='Made with discord.py', icon_url='https://i.imgur.com/oJjI5bp.png')
        await ctx.send(embed=em)


    @commands.command()
    async def invite(self, ctx):
        """Invite me to a new server =]"""
        await ctx.send('https://discordapp.com/oauth2/authorize?'
                       'client_id=353535708310536202&scope=bot&permissions=499477718')

    @commands.command()
    async def support(self, ctx):
        """Get Help/ Report bugs to my owner (he's the best owner)"""
        await ctx.send('Thor bot has a support server where you can get help on issues with the bot, join it here:\n'
                       'https://discord.gg/e5XApc5')


def setup(bot):
    bot.add_cog(Meta(bot))
