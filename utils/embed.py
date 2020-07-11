import discord
import datetime


def logger(target, punishment, executioner, reason="None", avatar_status=True):
    """Builds embed for audit logs"""
    if punishment == 'Kick':
        em_colour = 0xffff00
    elif punishment == 'Soft Ban':
        em_colour = 0xffaa00
    elif punishment == 'Ban':
        em_colour = 0xff0000
    elif punishment == 'Mute':
        em_colour = 0x9ACD32
    elif punishment == 'Unban':
        em_colour = 0x00A86B
    else:
        em_colour = 0x808080

    embed = discord.Embed(
        title=punishment,
        colour=discord.Colour(em_colour),
        description="\n\n",
        timestamp=datetime.datetime.utcnow()
    )
    embed.add_field(name=target, value=str(target.id), inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Moderator", value=executioner.mention, inline=False)
    if ("nsfw" not in reason.lower()) and avatar_status:
        embed.setd_thumbnail(url=target.avatar_url)

    return embed
