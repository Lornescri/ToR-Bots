import discord
import asyncio
import platform
import random

import reddit_stats
import time

import hangman
import passwords_and_tokens

MAINTENANCE = False

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

    await start_watching()


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

        if "send rudes" in message.content.lower():
            await client.send_message(message.channel, insult())


async def goodbad(message, args):
    if len(args) == 1:
        name = args[0]
    else:
        name = message.author.display_name

    name = get_redditor_name(name)
    await client.send_message(message.channel, "This may take a while")
    await client.send_message(message.channel, reddit_stats.goodbad(name))


async def torstats(message, name, args):
    """
    Displays statistics about transcriptions for TranscribersOfReddit.
    You can call it with or without a name to check.
    """
    await client.send_message(message.channel, "I'm only in beta, so forgive me for mistakes please"
                                               "\nSadly I can only see and count your last 1000 comments."
                                               "\nThe numbers can even be higher than your official Γ count, because "
                                               "I am just counting all of your comments that look like transcriptions.")

    if len(args) > 1:
        await client.send_message(message.channel, ":warning: Please give me one or no argument.")
    else:
        if len(args) == 1:
            name = args[0]

        name = get_redditor_name(name)

        embed = discord.Embed(title="Stats for /u/" + name,
                              description=reddit_stats.stats(name.replace("/u/", "").replace("u/", "").split(" ")[0]))
        await client.send_message(message.channel, embed=embed)


async def start_watching():
    for u in tor_server.members:
        print(u.display_name, reddit_stats.get_flair_count(get_redditor_name(u.display_name), 10))

    await client.send_message(fingerbit, "First round is done!")

    while True:
        try:
            await watch()
        except (KeyboardInterrupt, SystemExit):
            await client.close()
        except:
            print("------------- Error on watch -------------------")
            await asyncio.sleep(2)


async def watch():
    while True:
        nextit = set(tor_server.members)
        for u in nextit:
            await get_flair_count(get_redditor_name(u.display_name), u)
            await asyncio.sleep(0.1)

        # print(">> Starting again <<")


async def get_flair_count(name, u):
    global user_flairs

    reddit_name = get_redditor_name(name)
    count = reddit_stats.get_flair_count(reddit_name, 5)

    if count == -1:
        return

    if reddit_name not in user_flairs:
        print("New name: " + reddit_name)
        user_flairs[reddit_name] = count
    else:
        flair_count = count
        if flair_count > user_flairs[reddit_name]:
            await client.send_message(probechannel,
                                      name + " got from " + str(user_flairs[reddit_name]) + " to " + str(flair_count))
            await new_flair(name, user_flairs[reddit_name], flair_count, u)

            with open("transcription_log", "a") as dat:
                dat.write(" ".join(
                    [str(time.time()), name, reddit_stats.last_trans(name), str(user_flairs[reddit_name]), "->",
                     str(flair_count), "\n"]))
                dat.close()

            user_flairs[reddit_name] = flair_count


async def gammas(channel):
    returnstring = ""
    allTranscs = 0

    for name, flair in sorted(user_flairs.items(), key=lambda x: x[1], reverse=True):
        returnstring += name.replace("_", "\\_") + ": " + str(flair) + "\n"
        allTranscs += flair
        if len(returnstring) >= 1500:
            await client.send_message(channel, embed=discord.Embed(title="Official Γ count", description=returnstring))
            returnstring = ""

    returnstring += "Sum of all transcriptions: " + str(allTranscs) + " Γ"

    if len(returnstring) >= 1:
        await client.send_message(channel, embed=discord.Embed(title="Official Γ count", description=returnstring))
        returnstring = ""

    # embed = discord.Embed(title="Official Γ count", description=returnstring[:-1])
    # await client.send_message(channel, embed=embed)


async def new_flair(name, before, after, u):
    mention = u.mention
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
