import discord
import asyncio
import platform
import random

import database_reader
import time

import passwords_and_tokens

MAINTENANCE = True

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
    global probechannel
    global bot_commands
    global tor_server

    fingerbit = await client.get_user_info("256084554375364613")
    probechannel = client.get_channel("387401723943059460")
    bot_commands = client.get_channel("372168291617079296")
    tor_server = client.get_server("318873523579781132")

    print('Logged in as ' + client.user.name + ' (ID:' + client.user.id + ') | Connected to ' + str(
        len(client.servers)) + ' servers | Connected to ' + str(len(set(client.get_all_members()))) + ' users')
    print('--------')
    print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__,
                                                                               platform.python_version()))
    print('--------')
    print('Use this link to invite {}:'.format(client.user.name))
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(client.user.id))
    await client.send_message(fingerbit, "StatsBot online")

    await watch()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if MAINTENANCE and message.content.startswith("!") and message.author.name != "Fingerbit":
        await client.send_message(message.channel, ":warning: This bot is under maintenance, sorry. :warning:")
    else:
        if message.content.startswith("!torstats"):
            await torstats(message, message.author.display_name, message.content.split(" ")[1:])

        if message.content.startswith("!watch"):
            await watch()

        if message.content.startswith("!gammas"):
            await gammas(message.channel)

        if message.content == ("!restart stats"):
            if message.author == fingerbit:
                await client.send_message(message.channel, "Restarting StatsBot...")
                await client.close()
            else:
                await client.send_message(message.channel, "You have no power here!")

        if message.content.startswith("!goodbad"):
            await goodbad(message, message.content.split(" ")[1:])

        if "good bot" in message.content.lower():
            await client.add_reaction(message, u"\U0001F916")

        if "bad bot" in message.content.lower():
            await client.add_reaction(message, u"\U0001F622")

        if "jarvin" in message.content.lower():
            await client.add_reaction(message, u"\U0001F44D")

        if "send rudes" in message.content.lower():
            await client.send_message(message.channel, insult())


async def goodbad(message, args):
    pass #TODO


async def torstats(message, name, args):
    if len(args) > 1:
        await client.send_message(message.channel, ":warning: Please give me one or no argument.")
    else:
        if len(args) == 1:
            name = args[0]

        name = get_redditor_name(name)

        embed = discord.Embed(title="Stats for /u/" + name,
                              description=database_reader.stats(get_redditor_name(name)))
        await client.send_message(message.channel, embed=embed)


async def watch():
    lasttime = time.time()
    while True:
        nextit = set(tor_server.members)
        i = 0
        print("Iterating over", len(nextit), "users:")
        for u in nextit:
            i += 1
            if i % 50 == 0:
                print(i, end="")
            elif i % 10 == 0:
                print(".", end="")

            await add_user(u)

        for thing in database_reader.get_new_flairs(lasttime):
            print(thing)
            await new_flair(thing[0], thing[1], thing[2], thing[3])

        lasttime = time.time()
        await asyncio.sleep(10)
        print(" done")

        # print(">> Starting again <<")

async def add_user(u):
    database_reader.add_user(get_redditor_name(u.display_name), u.id)

async def gammas(channel):
    returnstring = ""
    allTranscs = 0

    for name, flair in sorted(database_reader.gammas(), key=lambda x: x[1], reverse=True):
        returnstring += name.replace("_", "\\_") + ": " + str(flair) + "\n"
        allTranscs += flair
        if len(returnstring) >= 1500:
            await client.send_message(channel, embed=discord.Embed(title="Official Γ count", description=returnstring))
            returnstring = ""

    returnstring += "Sum of all transcriptions: " + str(allTranscs) + " Γ"

    if len(returnstring) >= 1:
        await client.send_message(channel, embed=discord.Embed(title="Official Γ count", description=returnstring))
        returnstring = ""


async def new_flair(name, before, after, u):
    mention = (await client.get_user_info(u)).mention
    await client.send_message(probechannel, name + " got from " + str(before) + " to " + str(after))
    if not before == 0:
        if before < 51 <= after:
            await client.send_message(bot_commands, "Congrats to " + mention + " for their green flair!")
        if before < 101 <= after:
            await client.send_message(bot_commands, "Orange flair? Not bad, " + mention + "!")
        if before < 251 <= after:
            await client.send_message(bot_commands, mention + " got purple flair, amazing!")
        if before < 500 <= after:
            await client.send_message(bot_commands, "Give it up for the new owner of golden flair, " + mention + "!")
        if before < 1000 <= after:
            await client.send_message(bot_commands, "Holy guacamole, " + mention + " earned their diamond flair!")


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


def get_redditor_name(name):
    return name.replace("/u/", "").replace("u/", "").split(" ")[0]


client.run(passwords_and_tokens.discord_token)
