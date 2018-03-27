from discord.ext import commands

BOT_OWNERS=["256084554375364613", "193053876692189184"]

def is_owner(ctx):
    return ctx.message.author.id in BOT_OWNERS