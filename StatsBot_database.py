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

    refresh_leaderboard()
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

        if message.content.startswith("!allstats"):
            await allstats(message)

        if message.content.startswith("!serverinfo"):
            await client.send_message(message.channel, "This is a good server with good persons.")

        if message.content.startswith("!leaderboard"):
            await post_leaderboard(message.channel)

        if message.content.startswith("!where"):
            await findComments(message, message.author.display_name, " ".join(message.content.split(" ")[1:]))

        if message.content.startswith("!watch"):
            await watch()

        if message.content.startswith("!history"):
            await history(message, message.content.split(" ")[1:])

        if message.content.startswith("!context_history"):
            await history(message, message.content.split(" ")[1:], True)

        if message.content.startswith("!gammas"):
            await gammas(message.channel)

        if message.content.startswith("!permalink"):
            await client.send_message(message.channel,
                                      "https://reddit.com" + reddit.comment(message.content.split(" ")[1]).permalink)

        if message.content == ("!reset leaderboard"):
            if message.author == fingerbit:
                await client.send_message(message.channel, "Resetting leaderboard...")
                await reset_leaderboard()
            else:
                await client.send_message(message.channel, "You have no power here!")

        if message.content == ("!restart stats"):
            if message.author == fingerbit:
                await client.send_message(message.channel, "Restarting StatsBot...")
                await client.close()
            else:
                await client.send_message(message.channel, "You have no power here!")

        if message.content.startswith("!goodbad"):
            await client.send_message(message.channel, "This command is deprecated, you can just type '!torstats' now.")

        if "good bot" in message.content.lower():
            await client.add_reaction(message, u"\U0001F916")

        if "bad bot" in message.content.lower():
            await client.add_reaction(message, u"\U0001F622")

        if "jarvin" in message.content.lower():
            await client.add_reaction(message, u"\U0001F44D")

        if "send rudes" in message.content.lower():
            await client.send_message(message.channel, insult())


async def torstats(message, name, args):
    if len(args) > 1:
        await client.send_message(message.channel, ":warning: Please give me one or no argument.")
    else:
        if len(args) == 1:
            name = args[0]

        name = get_redditor_name(name)

        comment_count, official_gammas, trans_number, char_count, upvotes, good_bot, bad_bot, good_human, bad_human, valid = database_reader.stats(
            name)

        if valid is None:
            await client.send_message(message.channel, "I didn't know that user, try again in about {} seconds.".format(
                database_reader.info()[2]))
            await add_user(name, None)
            return
        elif not valid:
            await client.send_message(message.channel,
                                      "That user is invalid, tell {} if you don't think so.".format(fingerbit.mention))
        elif official_gammas is None or official_gammas == 0:
            await client.send_message(message.channel, "That user has no transcriptions")

        output = ("*I counted {} of your total comments*\n"
                  "**Official Γ count**: {} (~ {})\n"
                  "**Number of transcriptions I see**: {}\n"
                  "**Total characters**: {}   (*{} per transc.*)\n"
                  "**Total upvotes**: {}   (*{} per transc.*)\n"
                  "**Good Bot**: {}   (*{} per transc.*)\n"
                  "**Bad Bot**: {}   (*{} per transc.*)\n"
                  "**Good Human**: {}   (*{} per transc.*)\n"
                  "**Bad Human**: {}   (*{} per transc.*)".format(
            comment_count, official_gammas,
            str(round(official_gammas / database_reader.kumas(),
                      2)) + " KLJ" if official_gammas / database_reader.kumas() >= 1
            else str(round(1000 * official_gammas / database_reader.kumas(), 2)) + " mKLJ",
            trans_number, char_count, round(char_count / trans_number, 2), upvotes,
            round(upvotes / trans_number, 2), good_bot, round(good_bot / trans_number, 2), bad_bot,
            round(bad_bot / trans_number, 2),
            good_human, round(good_human / trans_number, 2), bad_human, round(bad_human / trans_number, 2)))

        embed = discord.Embed(title="Stats for /u/" + name,
                              description=output)
        await client.send_message(message.channel, embed=embed)


async def allstats(message):
    trans_count, total_length, upvotes, good_bot, bad_bot, good_human, bad_human = database_reader.all_stats()

    output = ("*Number of transcriptions I see: {}*\n"
              "**Total Γ count**: {} (~ {} KLJ)\n"
              "**Character count**: {}\n"
              "**Upvotes**: {}\n"
              "**Good Bot**: {}\n"
              "**Bad Bot**: {}\n"
              "**Good Human**: {}\n"
              "**Bad Human**: {}".format(
        trans_count, database_reader.get_total_gammas(),
        round(database_reader.get_total_gammas() / database_reader.kumas(), 2),
        total_length, upvotes, good_bot, bad_bot, good_human, bad_human))

    embed = discord.Embed(title="Stats for everyone on Discord", description=output)
    await client.send_message(message.channel, embed=embed)


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


async def findComments(message, display_name, param):
    results = database_reader.find_comments(get_redditor_name(display_name), param)
    if len(results) == 0:
        await client.send_message(message.channel, "No matching transcription found")
    elif len(results) > 10:
        await client.send_message(message.channel, "More than 10 transcriptions found")
    else:
        await client.send_message(message.channel,
                                  "**Results**:\n" + "\n".join(["```...{}...```\n<https://www.reddit.com{}>".format(
                                      content[content.lower().find(param.lower()) - 10: content.lower().find(
                                          param.lower()) + len(param) + 10],
                                      reddit.comment(link).permalink) for link, content in results]))


async def add_user(u, id):
    database_reader.add_user(get_redditor_name(u), id)


async def post_leaderboard(channel):
    with open("leaderboard.txt", "a") as dat:
        msg = await client.send_message(channel, "Waiting for refresh...")
        dat.write(msg.id + " " + msg.channel.id + "\n")

    refresh_leaderboard()


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


async def history(msg, args, whole=False):
    if len(args) > 1:
        await client.send_message(msg.channel, ":warning: Please give me one or no argument.")
        return

    if len(args) == 0:
        name = msg.author.display_name

    else:
        name = args[0]

    path = database_reader.plot_history(get_redditor_name(name), whole)
    if not path:
        await client.send_message(msg.channel, "No history avaliable, sorry!")

    else:
        await client.send_file(msg.channel, path)


async def gammas(channel):
    returnstring = ""
    allTranscs = 0
    count = 0

    for name, flair in sorted(database_reader.gammas(), key=lambda x: x[1], reverse=True):
        count += 1
        returnstring += str(count) + ". " + name.replace("_", "\\_") + ": " + str(flair) + "\n"
        allTranscs += flair
        if count % 25 == 0:
            await asyncio.sleep(0.5)
            await client.send_message(channel,
                                      embed=discord.Embed(title="Official Γ count", description=returnstring))
            returnstring = ""

    returnstring += "Sum of all transcriptions: " + str(allTranscs) + " Γ"

    if len(returnstring) >= 1:
        await asyncio.sleep(0.5)
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
            await client.send_message(bot_commands,
                                      "Give it up for the new owner of golden flair, " + mention + "!")
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
