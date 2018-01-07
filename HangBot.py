# This bot is offline at the moment, because it always crashes

import discord
import asyncio
import platform

import reddit_stats
import hangman
import passwords_and_tokens

MAINTENANCE = False

client = discord.Client()
fingerbit = None

guesser = None

user_flairs = dict()


@client.event
async def on_ready():
    global fingerbit

    fingerbit = await client.get_user_info("256084554375364613")

    print('Logged in as ' + client.user.name + ' (ID:' + client.user.id + ') | Connected to ' + str(
        len(client.servers)) + ' servers | Connected to ' + str(len(set(client.get_all_members()))) + ' users')
    print('--------')
    print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__,
                                                                               platform.python_version()))
    print('--------')
    print('Use this link to invite {}:'.format(client.user.name))
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(client.user.id))
    await client.send_message(fingerbit, "HangBot online")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if MAINTENANCE and message.content.startswith("!") and message.author.name != "Fingerbit":
        # await client.send_message(message.channel, ":warning: This bot is under maintenance, sorry. :warning:")
        pass
    else:
        if message.content.startswith("!newgame"):
            await newgame(message, message.content.split(" ")[1:])

        if message.content.startswith("!hang"):
            await hang(message, message.content.split(" ")[1:])

        if message.author == fingerbit and  message.content == "!restart hang":
            await client.close()


async def newgame(message, args):
    """
    Start a game of hangman.
    """
    global guesser

    if len(args) != 1 or args[0] not in ["english", "german"]:
        await client.send_message(message.channel,
                                  "Please select a language with *!newgame english* or *!newgame german*.")
        return

    # TODO
    if message.author.name != "Fingerbit" and args[0] == "german":
        await client.send_message(message.channel, "German is not available at the moment, sorry.")
        return

    await client.send_message(message.channel, "***Let's play hangman!***")
    try:
        guesser = hangman.Guesser(args[0])
    except:
        await client.close()
    await client.send_message(message.channel,
                              "Heyo! I'm in beta, so please be nice :grinning:\n\n**Rules**\n- Use . for letters I have not guessed yet."
                              "\n- If I guess something, the next input should be the word with the guess revealed"
                              "\n\n**Example**:\n!hang .....\n*I guess 'e'*\n!hang ..e.e\n*I guess 'n'*\n!hang ..e.e\nYou get the idea.")


async def hang(message, args):
    """
    Let me guess in hangman.
    """
    global guesser
    if guesser is None:
        await client.send_message(message.channel, "Please start a new Game with !newgame <language>")
    elif len(args) != 1:
        await client.send_message(message.channel, ":warning: Please give me only one Argument")
    else:
        nextout, nextprint = guesser.guess(args[0].replace(" ", "").replace(".", "_"))
        await client.send_message(message.channel, nextprint)
        if nextout is None or len(nextout) > 1:
            guesser = None

client.run(passwords_and_tokens.discord_token)
