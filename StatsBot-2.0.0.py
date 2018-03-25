from discord.ext import commands
import passwords_and_tokens

description = '''A bot to show your ToR stats on the discord.'''

# this specifies what extensions to load when the bot starts up
startup_extensions = ["sb-textcommands", "sb-graphs", "sb-admin", "sb-reactions", "sb-routines"]

bot = commands.Bot(command_prefix='!', description=description)



@bot.command()
async def load(extension_name : str):
    """Loads an extension."""
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await bot.say("{} loaded.".format(extension_name))

@bot.command()
async def unload(extension_name : str):
    """Unloads an extension."""
    bot.unload_extension(extension_name)
    await bot.say("{} unloaded.".format(extension_name))


if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

bot.run(passwords_and_tokens.discord_token)