import discord, asyncio, time, platform
from discord.ext import commands
import database_reader, passwords_and_tokens
import praw, random

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



class ReactionsReactor():
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        if "good bot" in message.content.lower():
            await self.bot.add_reaction(message, u"\U0001F916")

        if "bad bot" in message.content.lower():
            await self.bot.add_reaction(message, u"\U0001F622")

        if "jarvin" in message.content.lower():
            await self.bot.add_reaction(message, u"\U0001F44D")

        if "send rudes" in message.content.lower():
            await self.bot.send_message(message.channel, insult())
    
def setup(bot):
    bot.add_cog(ReactionsReactor(bot))

