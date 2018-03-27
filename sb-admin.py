import discord, asyncio, time, platform, socket, datetime
from discord.ext import commands
import database_reader, passwords_and_tokens
import praw
from permission import is_owner


reddit = praw.Reddit(client_id=passwords_and_tokens.reddit_id, client_secret=passwords_and_tokens.reddit_token,
                     user_agent="Lornebot 0.0.1")


def get_redditor_name(name):
    return name.replace("/u/", "").replace("u/", "").split(" ")[0]

async def add_user(u, id):
    database_reader.add_user(get_redditor_name(u), id)

cogload = time.time()



class Administration():
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self): # no decorator needed, https://stackoverflow.com/questions/48038953/bot-event-in-a-cog-discord-py
        # SET probechannel and botcommands

        bootup = self.bot.get_channel("428212915473219604")

        await self.bot.send_message(bootup, "<@&428212811290771477>", embed=discord.Embed(
            title="StatsBot Booted",
            description=f"Booted in {round(time.time() - cogload)}s on hostname {socket.gethostname()}",
            colour=0x00FF00,
            timestamp=datetime.datetime.now()
        ))
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
    async def ping(self):
        await self.bot.say("Pong!")
    
def setup(bot):
    bot.add_cog(Administration(bot))

