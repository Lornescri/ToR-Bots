import discord, asyncio, time, platform
from discord.ext import commands
import database_reader, passwords_and_tokens
import praw

BOT_OWNER="193053876692189184" # TODO: Get owner from bot owner set in main file


def owner(ctx):
    if ctx.message.author.id == BOT_OWNER:
        return True
    return False

bot_commands = None
probechannel = None
tor_server = None
owner_person = None

reddit = praw.Reddit(client_id=passwords_and_tokens.reddit_id, client_secret=passwords_and_tokens.reddit_token,
                     user_agent="Lornebot 0.0.1")


def get_redditor_name(name):
    return name.replace("/u/", "").replace("u/", "").split(" ")[0]

async def add_user(u, id):
    database_reader.add_user(get_redditor_name(u), id)




class Administration():
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self): # no decorator needed, https://stackoverflow.com/questions/48038953/bot-event-in-a-cog-discord-py
        # SET probechannel and botcommands
        probechannel = self.bot.get_channel("387401723943059460")
        bot_commands = self.bot.get_channel("372168291617079296")
        tor_server = self.bot.get_server("318873523579781132")
        owner_person = await self.bot.get_user_info(BOT_OWNER)

        await self.bot.send_message(owner_person, "StatsBot online")
        servers=len(self.bot.servers)
        pl = "s" if servers > 1 else ""
        print("=====================")
        print(f"Logged in as {self.bot.user.name} (ID: {self.bot.user.id}). Connected to"
              f" {servers} server{pl} | Connected to {len(set(self.bot.get_all_members()))} users.\n"
              f"--------------\n"
              f"Current Discord.py Version: {discord.__version__} | Current Python Version: {platform.python_version()}\n"
              f"--------------\n"
              f"Use this link to invite me: https://discordapp.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot&permissions=8\n"
              f"=====================")

    async def __local_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    @commands.check(owner)
    async def ping(self):
        await self.bot.say("Pong!")
    
def setup(bot):
    bot.add_cog(Administration(bot))

