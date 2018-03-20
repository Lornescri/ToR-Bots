import discord, asyncio
from discord.ext import commands
import database_reader

def get_redditor_name(name):
    return name.replace("/u/", "").replace("u/", "").split(" ")[0]

async def add_user(u, id):
    database_reader.add_user(get_redditor_name(u), id)

class TextCommands():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def torstats(self, ctx, person:str = None):
        name = person if person else get_redditor_name(ctx.message.author.display_name)
        comment_count, official_gammas, trans_number, char_count, upvotes, good_bot, bad_bot, good_human, bad_human, valid = database_reader.stats(name)

        if valid is None:
            await self.bot.send_message(ctx.message.channel, "I don't know that user, sorry!")
            await add_user(name, None)
            return
        elif not valid:
            await self.bot.send_message(ctx.message.channel,
                                      "That user is invalid, tell {} if you don't think so.".format(fingerbit.mention))
        elif official_gammas is None or official_gammas == 0:
            await self.bot.send_message(ctx.message.channel, "That user has no transcriptions")

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
        await self.bot.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True)
    async def allstats(self, ctx):
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
        await self.bot.send_message(ctx.message.channel, embed=embed)
    
    @commands.command()
    async def serverinfo(self):
        await self.bot.say("This is a good server with good persons")

    @commands.command(pass_context=True)
    async def gammas(self, ctx):
        channel = ctx.message.channel
        returnstring = ""
        allTranscs = 0
        count = 0

        for name, flair in sorted(database_reader.gammas(), key=lambda x: x[1], reverse=True):
            count += 1
            returnstring += str(count) + ". " + name.replace("_", "\\_") + ": " + str(flair) + "\n"
            allTranscs += flair
            if count % 25 == 0:
                await asyncio.sleep(0.5)
                await self.bot.send_message(channel,
                                        embed=discord.Embed(title="Official Γ count", description=returnstring))
                returnstring = ""

        returnstring += "Sum of all transcriptions: " + str(allTranscs) + " Γ"

        if len(returnstring) >= 1:
            await asyncio.sleep(0.5)
            await self.bot.send_message(channel, embed=discord.Embed(title="Official Γ count", description=returnstring))
            returnstring = ""


def setup(bot):
    bot.add_cog(TextCommands(bot))