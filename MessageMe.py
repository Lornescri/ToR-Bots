import discord
import asyncio
import platform

import reddit_stats
import hangman
import sys
import passwords_and_tokens

client = discord.Client()
fingerbit = None
probechannel = None
bot_commands = None
tor_server = None

guesser = None

user_flairs = dict()


@client.event
async def on_ready():
    global fingerbit

    fingerbit = await client.get_user_info("256084554375364613")

    message = " ".join(sys.argv[1:])

    await client.send_message(fingerbit, message)
    await client.close()

client.run(passwords_and_tokens.discord_token)
