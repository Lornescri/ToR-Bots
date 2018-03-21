import discord, asyncio
from discord.ext import commands
import database_reader

def get_redditor_name(name):
    return name.replace("/u/", "").replace("u/", "").split(" ")[0]

async def add_user(u, id):
    database_reader.add_user(get_redditor_name(u), id)

class GraphCommands():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def history(self, ctx, person:str = None):
        name = get_redditor_name(person) if person else get_redditor_name(ctx.message.author.display_name)
        path = database_reader.plot_history(get_redditor_name(name), False)
        if not path:
            await self.bot.send_message(ctx.message.channel,
                                    "No history avaliable, sorry! (*You have to do 2 transcriptions since joining the discord server*)")
        else:
            await self.bot.send_file(ctx.message.channel, path)

    @commands.command(pass_context=True)
    async def context_history(self, ctx, person:str = None):
        name = get_redditor_name(person) if person else get_redditor_name(ctx.message.author.display_name)
        path = database_reader.plot_history(get_redditor_name(name), True)
        if not path:
            await self.bot.send_message(ctx.message.channel,
                                    "No history avaliable, sorry! (*You have to do 2 transcriptions since joining the discord server*)")
        else:
            await self.bot.send_file(ctx.message.channel, path)

    @commands.command(pass_context=True)
    async def all_history(self, ctx):
        path = database_reader.all_history()
        if not path:
            await self.bot.send_message(ctx.message.channel,
                                    "No history avaliable, sorry!")

        else:
            await self.bot.send_file(ctx.message.channel, path)

def setup(bot):
    bot.add_cog(GraphCommands(bot))