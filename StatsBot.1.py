import discord
import asyncio
import platform
import random

import praw

import database_reader
import time

import passwords_and_tokens

MAINTENANCE = False

client = discord.Client()
reddit = praw.Reddit(client_id=passwords_and_tokens.reddit_id, client_secret=passwords_and_tokens.reddit_token,
                     user_agent="Lornebot 0.0.1")

fingerbit = None
probechannel = None
bot_commands = None
tor_server = None

guesser = None

user_flairs = dict()

    


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if MAINTENANCE and message.content.startswith("!") and message.author.name != "Fingerbit":
        await client.send_message(message.channel, ":warning: This bot is under maintenance, sorry. :warning:")
    else:

        if "good bot" in message.content.lower():
            await client.add_reaction(message, u"\U0001F916")

        if "bad bot" in message.content.lower():
            await client.add_reaction(message, u"\U0001F622")

        if "jarvin" in message.content.lower():
            await client.add_reaction(message, u"\U0001F44D")

        if "send rudes" in message.content.lower():
            await client.send_message(message.channel, insult())





async def watch():
    lasttime = time.time()
    while True:
        nextit = set(tor_server.members)
        print(".")
        for u in nextit:
            await add_user(u.display_name, u.id)

        gammas_changed = False
        for thing in database_reader.get_new_flairs(lasttime):
            gammas_changed = True
            await new_flair(thing[0], thing[1], thing[2], thing[3])

        if gammas_changed:
            print("r", end="")
            await refresh_leaderboard()

        lasttime = time.time()
        await asyncio.sleep(10)





async def add_user(u, id):
    database_reader.add_user(get_redditor_name(u), id)


async def post_leaderboard(channel):
    with open("leaderboard.txt", "a") as dat:
        msg = await client.send_message(channel, "Waiting for refresh...")
        dat.write(msg.id + " " + msg.channel.id + "\n")

    await refresh_leaderboard()


async def refresh_leaderboard():
    returnstring = "**Leaderboard**\n\n"
    count = 0

    for name, flair in sorted(database_reader.gammas(), key=lambda x: x[1], reverse=True)[:50]:
        count += 1
        returnstring += str(count) + ". " + name.replace("_", "\\_") + ": " + str(flair) + "\n"

    returnstring += "\n*This Message will be refreshed to always be up-to-date*"

    with open("leaderboard.txt", "r") as dat:
        for line in dat.readlines():
            line = line.strip()
            if (not line == ""):
                msg, channel = line.split(" ")
                cha = client.get_channel(channel)
                m = await client.get_message(cha, msg)
                await client.edit_message(m, returnstring)


async def reset_leaderboard():
    open("leaderboard.txt", "w").close()



async def new_flair(name, before, after, u):
    mention = (await client.get_user_info(u)).mention
    await client.send_message(probechannel, name + " got from " + str(before) + " to " + str(after))
    if not before == 0:
        if before < 51 <= after:
            await client.send_message(bot_commands, "Congrats to " + mention + " for their green flair!")
        if before < 101 <= after:
            await client.send_message(bot_commands, "Teal flair? Not bad, " + mention + "!")
        if before < 251 <= after:
            await client.send_message(bot_commands, mention + " got purple flair, amazing!")
        if before < 501 <= after:
            await client.send_message(bot_commands,
                                      "Give it up for the new owner of golden flair, " + mention + "!")
        if before < 1001 <= after:
            await client.send_message(bot_commands, "Holy guacamole, " + mention + " earned their diamond flair!")
        if before < 2501 <= after:
            await client.send_message(bot_commands, "Ruby flair! " + mention + ", that is absolutely amazing!")


def insult():
    column1 = []
    column2 = []
    column3 = []

    # Read contents of column1.txt and add the contents to the 1st list
    file1 = open("column1.txt", "r")
    line = file1.readline()
    while line != "":
        column1.append(line.strip())
        line = file1.readline()
    file1.close()

    # Read contents of column2.txt and add the contents to the 2nd list
    file2 = open("column2.txt", "r")
    line = file2.readline()
    while line != "":
        column2.append(line.strip())
        line = file2.readline()
    file2.close()

    # Read contents of column3.txt and add the contents to the 3rd list
    file3 = open("column3.txt", "r")
    line = file3.readline()
    while line != "":
        column3.append(line.strip())
        line = file3.readline()
    file3.close()

    return "Thou " + column1[random.randint(0, 49)] + " " + column2[random.randint(0, 49)] + " " + column3[
        random.randint(0, 49)] + "!"





client.run(passwords_and_tokens.discord_token)
