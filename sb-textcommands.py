import discord, asyncio
from discord.ext import commands
import database_reader, passwords_and_tokens
import praw
from util import Pages, CannotPaginate


reddit = praw.Reddit(client_id=passwords_and_tokens.reddit_id, client_secret=passwords_and_tokens.reddit_token,
                     user_agent="Lornebot 0.0.1")


def get_redditor_name(name):
    return name.replace("/u/", "").replace("u/", "").split(" ")[0]

async def add_user(u, id):
    database_reader.add_user(get_redditor_name(u), id)

def minutesToHuman(minutes):
    days = 0
    hours = 0
    mins = 0

    while minutes >= (60 * 24):
        minutes -= (60 * 24)
        days += 1

    while minutes >= 60:
        minutes -= 60
        hours += 1

    mins += minutes
    s = f"{str(days) + ' days, ' if days else ''}{str(hours) + ' hours, ' if hours else ''}{str(mins) + ' minutes.' if mins else ''}"

    sList = list(s)

    if sList[-2] + sList[-1] == ", ":
        sList[-1] = ""
        sList[-2] = ""

    s = "".join(sList)

    return s
    
class TextCommands():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def torstats(self, ctx, person:str = None):
        name = get_redditor_name(person) if person else get_redditor_name(ctx.message.author.display_name)
        comment_count, official_gammas, trans_number, char_count, upvotes, good_bot, bad_bot, good_human, bad_human, valid = database_reader.stats(name)

        if valid is None:
            await self.bot.send_message(ctx.message.channel, "I don't know that user, sorry!")
            await add_user(name, None)
            return
        elif not valid:
            await self.bot.send_message(ctx.message.channel,
                                      "That user is invalid, tell Lornescri if you don't think so.")
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
    @commands.command()
    async def permalink(self, thread: str):
        await self.bot.say("https://reddit.com" + reddit.comment(thread).permalink)

    @permalink.error
    async def permalink_error(self, ctx, error):
        await self.bot.say("That made an error! Are you sure you provided a valid ID?")

    @commands.command()
    async def goodbad(self):
        await self.bot.say("This command is deprecated, you can just type '!torstats' now.")


    @commands.command(pass_context=True)
    async def where(self, ctx, *args):
        lookingFor = " ".join(args)
        results = database_reader.find_comments(get_redditor_name(ctx.message.author.display_name), lookingFor)

        entries = [
            f"https://reddit.com{reddit.comment(link).permalink}\n```...{content[content.lower().find(lookingFor.lower()) - 10: content.lower().find(lookingFor.lower()) + len(lookingFor) + 10]}...```"
            for link, content in results
        ]

        await Pages(self.bot, message=ctx. message, entries=entries, per_page=5).paginate(start_page=1)

    @commands.command(pass_context=True)
    async def where(self, ctx, *args):
        lookingFor = " ".join(args)
        results = database_reader.find_comments(get_redditor_name(ctx.message.author.display_name), lookingFor, all=True)

        entries = [
            f"https://reddit.com{reddit.comment(link).permalink}\n```...{content[content.lower().find(lookingFor.lower()) - 10: content.lower().find(lookingFor.lower()) + len(lookingFor) + 10]}...```"
            for link, content in results
        ]

        await Pages(self.bot, message=ctx. message, entries=entries, per_page=5).paginate(start_page=1)

    @commands.command(pass_context=True)
    async def progress(self, ctx, person:str=None):
        """
        Returns your progress along the 100/24 way
        """

        progress_bar = "[----------]"
        name = get_redditor_name(person) if person else get_redditor_name(ctx.message.author.display_name)
        rows = database_reader.get_last_x_hours(name, 24)
        #rows = list(range(130))
        bars = int((len(rows) / 10) - ((len(rows) / 10) % 1)) # Gets progress out of 10 (can be higher than 10)
        
        if len(rows) == 0:
            out = "`[----------]` - You know exactly how many you've done, you slacker."
        elif len(rows) < 100:
            for i in range(bars):
                print(i)
                a = [x for x in progress_bar]
                a[i+1] = "#"
                progress_bar = "".join(a)
            
            out = f"`{progress_bar}` - You've done {len(rows)} transcriptions in the last 24 hours. Keep going, you can do it!"

        elif len(rows) == 100:
            out = f"`[##########]` - The little one has only gone and done it! You've done {len(rows)} / 24 :D"
        else:
            out = f"`[##########]####` - holy hecc, you've done {len(rows)} transcriptions in 24 hours :O. That's a lot of transcriptions in 24 hours"

        await self.bot.say(out)

    @commands.command(pass_context=True)
    async def until(self, ctx, future_gamma:int):
        name = get_redditor_name(ctx.message.author.display_name)
        rows = database_reader.get_last_x_hours(name, 48)
        # Over 48 hours to give most accurate results (hopefully)

        #row["counted_comments"], row["official_gamma_count"], row["comment_count"], row["total_length"], upvotes,
        # good_bot, bad_bot, good_human, bad_human, row["valid"]
        x, gamma, a, b, c, d, e, f, g, h = database_reader.stats(name) # ignore everything except gamma count

        difference = future_gamma - gamma 
        if difference <= 0:
            return await self.bot.say("Please provide a gamma that's higher than your current count 😛")

        # is person jabba?
        if len(rows) == 0:
            motivation = 'to get your butt into gear and start transcribing ;)' if ctx.message.author.id == '280001404020588544' else 'to get to Γ' + str(future_gamma) + ' (you haven\'t done any in the past 48 hours)'
            return await self.bot.say(f"From your rate over the past 48 hours, I estimate that it will take you `∞ days, ∞ hours, ∞ minutes` {motivation}")

        rate_per_minute = len(rows) / ( 2 * 24 * 60 ) # turn from transcriptions per 48hr to per minute

        minutes = round(difference / rate_per_minute)

        time_ = minutesToHuman(minutes)

        await self.bot.say(f"From your rate over the past 48 hours, I estimate that it will take you `{time_}` to get from Γ{gamma} to Γ{future_gamma}")





def setup(bot):
    bot.add_cog(TextCommands(bot))