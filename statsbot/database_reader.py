import pymysql, time
import matplotlib, datetime
matplotlib.use("AGG")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import passwords_and_tokens

def getConnection():
    return pymysql.connect(host=passwords_and_tokens.sql_ip,
                             user=passwords_and_tokens.sql_user,
                             password=passwords_and_tokens.sql_password,
                             db="torstats",
                             charset="utf8mb4",
                             cursorclass=pymysql.cursors.DictCursor,
                             port=3306)


def get_flair_count(reddit_name, discord_id):
    connection = getConnection()
    with connection.cursor() as cursor:
        cursor.execute("select * from transcribers where name = %s", (reddit_name,))
        if cursor.rowcount < 1:
            add_user(reddit_name, discord_id)
            return -1

        row = cursor.fetchone()

        if not row["valid"] or row["official_gamma_count"] is None:
            return -1
    connection.close()
    return row["official_gamma_count"]


def get_last_x_hours(reddit_name, hours=24):
    connection = getConnection()
    with connection.cursor() as cursor:
        cursor.execute("select * from transcriptions where transcriber = %s", (reddit_name,))
        rows = cursor.fetchall()

    if len(rows)==0:
        return None

    rows = [x for x in rows if x["created"] > datetime.datetime.now()-datetime.timedelta(hours=hours)]
    connection.close()
    return rows


def all_history():
    connection = getConnection()
    with connection.cursor() as cursor:
        cursor.execute("select sum(new_gamma-old_gamma) as difs from new_gammas")
        total = get_total_gammas() - cursor.fetchone()["difs"]

        cursor.execute("select new_gamma - old_gamma as dif, time from new_gammas")

        rows = cursor.fetchall()
        
    vals = list()
    times = list()

    for dif, time in [(row["dif"], row["time"]) for row in rows]:
        total += dif
        vals.append(total)
        times.append(time)

    plt.plot(times, vals, color="black")
        
    plt.xlabel("Time")
    plt.ylabel("Gammas")
    plt.xticks(rotation=90)
    plt.gcf().subplots_adjust(bottom=0.3)
    plt.title("Server Gamma History")
    plt.savefig("graph.png")
    plt.clf()
    connection.close()
    return "graph.png"

def plot_multi_history(people):
    connection = getConnection()
    most = 0
    cols = ["black", "green", "red", "teal", "purple", "gold", "deeppink"]
    for i, name in enumerate(people):
        with connection.cursor() as cursor:
            cursor.execute("select * from new_gammas where transcriber = %s", (name,))
            rows = cursor.fetchall()

        times = [row["time"] for row in rows]
        values = [row["new_gamma"] for row in rows]
        if len(values) < 2:
            return False
        if values[-1] > most: most = values[-1]
        plt.plot(times, values, color=cols[i])
    
    #first = values[0]
    #last = values[-1] 
    whole = False
    if whole or most >= 50: 
        plt.axhline(y=51, color="lime") 
    if whole or 100 < most:
        plt.axhline(y=101, color="teal")
    if whole or 250 < most: 
        plt.axhline(y=251, color="purple")
    if whole or 500 < most:
        plt.axhline(y=501, color="gold")
    if whole or 1000 <= most: 
        plt.axhline(y=1000, color="aqua")
    if whole or most >= 2500:
        plt.axhline(y=2500, color="deeppink")
    plt.xlabel("Time") 
    plt.ylabel("Gammas")
    plt.legend(people)
    plt.xticks(rotation=90) 
    plt.gcf().subplots_adjust(bottom=0.3)
    plt.title("Multi-gamma history") 
    plt.savefig("graph.png")
    plt.clf()
    connection.close()
    return "graph.png"

def plot_distribution():
    connection = getConnection()
    with connection.cursor() as cursor:
        cursor.execute("select official_gamma_count from transcribers where official_gamma_count is not NULL and official_gamma_count > 0")
        rows = cursor.fetchall()

    rows = [row["official_gamma_count"] for row in rows]
    rows.sort()
    plt.title("Gamma distribution")
    plt.plot(rows)
    plt.savefig("graph.png")
    plt.clf()
    connection.close()
    return "graph.png"

def plot_rate(name):
    connection = getConnection()
    with connection.cursor() as cursor:
        cursor.execute("select * from new_gammas where transcriber = %s", (name,))
        rows = cursor.fetchall()


    # Code gets number of days between when the bot was first collecting data, to now
    start = datetime.datetime(2017, 11, 1)
    end = datetime.datetime.now()
    step = datetime.timedelta(days=1)

    result = []
    while start < end:
        result.append(start)
        start += step
    
    # Create new subplot because some funcs only work on subplots
    fig, ax = plt.subplots(1,1) 

    # Create dataset; a list of datetime objects
    x = [mdates.epoch2num(time.mktime(row["time"].timetuple())) for row in rows]
    
    # Make
    ax.hist(x, len(result))
    # Set date format to be a bit shorter
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%y'))

    # Rotate labels 90^o
    ax.xaxis.set_tick_params(labelrotation=90.0)

    # Don't cut off date
    plt.gcf().subplots_adjust(bottom=0.22)

    # Standard code
    plt.xlabel("Time")
    plt.ylabel("Gammas / Day")
    plt.title("Gamma gain rate of /u/{}".format(name))
    plt.savefig("graph.png")
    plt.clf()
    connection.close()
    return "graph.png"

def plot_all_rate():
    connection = getConnection()
    with connection.cursor() as cursor:
        cursor.execute("select * from new_gammas")
        rows = cursor.fetchall()


    # Code gets number of days between when the bot was first collecting data, to now
    start = datetime.datetime(2017, 11, 1)
    end = datetime.datetime.now()
    step = datetime.timedelta(days=1)

    result = []
    while start < end:
        result.append(start)
        start += step
    
    # Create new subplot because some funcs only work on subplots
    fig, ax = plt.subplots(1,1) 

    # Create dataset; a list of datetime objects
    x = [mdates.epoch2num(time.mktime(row["time"].timetuple())) for row in rows]
    
    # Make
    ax.hist(x, len(result))
    # Set date format to be a bit shorter
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%y'))

    # Rotate labels 90^o
    ax.xaxis.set_tick_params(labelrotation=90.0)

    # Don't cut off date
    plt.gcf().subplots_adjust(bottom=0.22)

    # Standard code
    plt.xlabel("Time")
    plt.ylabel("Gammas / Day")
    plt.title("Gamma gain rate of the whole server")
    plt.savefig("graph.png")
    plt.clf()
    connection.close()
    return "graph.png"


def get_total_gammas():
    connection = getConnection()
    with connection.cursor() as cursor:
        cursor.execute("select sum(official_gamma_count) as gamma_count from transcribers")
        a = cursor.fetchone()["gamma_count"]
    connection.close()
    return a


def gammas():
    connection = getConnection()
    with connection.cursor() as cursor:
        cursor.execute("select name, official_gamma_count from transcribers where not official_gamma_count is null")
        x = cursor.fetchall()
    connection.close()
    return [(row["name"], row["official_gamma_count"]) for row in x]


def kumas():
    connection = getConnection()
    with connection.cursor() as cursor:
        cursor.execute("select official_gamma_count from transcribers where name = 'kumalumajuma'")
        x = cursor.fetchone()["official_gamma_count"]
    connection.close()
    return x


def stats(name):
    connection = getConnection()
    with connection.cursor() as cursor:
        cursor.execute(
            "select official_gamma_count, counted_comments, count(comment_id) as comment_count, sum(length(content)) as total_length,"
            "sum(upvotes) as upvotes, sum(good_bot) as good_bot, sum(bad_bot) as bad_bot, "
            "sum(good_human) as good_human, sum(bad_human) as bad_human, valid from transcribers "
            "left outer join transcriptions on name = transcriber where name = %s group by name",
            (name,))
        row = cursor.fetchone()

    if row is None:
        return (None,) * 10

    if row["upvotes"] is None:
        upvotes, good_bot, bad_bot, good_human, bad_human = 0, 0, 0, 0, 0
    else:
        upvotes, good_bot, bad_bot, good_human, bad_human = row["upvotes"], row["good_bot"], row["bad_bot"], row[
            "good_human"], row["bad_human"]
    connection.close()
    return (
        row["counted_comments"], row["official_gamma_count"], row["comment_count"], row["total_length"], upvotes,
        good_bot, bad_bot, good_human, bad_human, row["valid"])


def info():
    connection = getConnection()
    with connection.cursor() as cursor:
        cursor.execute("select * from info;")
        row = cursor.fetchone()
    connection.close()
    return row["most_recent"], row["least_recent"], row["difference"], row["running"]


def all_stats():
    connection = getConnection()
    with connection.cursor() as cursor:
        cursor.execute(
            "select count(comment_id) as comment_count, sum(length(content)) as total_length,"
            "sum(upvotes) as upvotes, sum(good_bot) as good_bot, sum(bad_bot) as bad_bot, "
            "sum(good_human) as good_human, sum(bad_human) as bad_human from transcriptions")
        row = cursor.fetchone()
    connection.close()
    return (row["comment_count"], row["total_length"], row["upvotes"],
            row["good_bot"], row["bad_bot"], row["good_human"], row["bad_human"])


def get_new_flairs(last_time):
    connection = getConnection()
    with connection.cursor() as cursor:
        cursor.execute(
            "select name, old_gamma, new_gamma, discord_id from new_gammas inner join transcribers on name = transcriber"
            " where unix_timestamp(time) > %s", (last_time,))
    connection.close()
    return [(row["name"], row["old_gamma"], row["new_gamma"], row["discord_id"]) for row in cursor.fetchall()]


def add_user(usr, discord_id):
    connection = getConnection()
    with connection.cursor() as cursor:
        cursor.execute("insert ignore into transcribers (name, discord_id) values (%s, %s)", (usr, discord_id))
    connection.commit()
    connection.close()


def get_transcriptions(name):
    connection = getConnection()
    with connection.cursor() as cursor:
        cursor.execute("select comment_id from transcriptions where transcriber = %s", (name,))

        x = [row["comment_id"] for row in cursor.fetchall()]
    connection.close()
    return x


def find_comments(name, text, all=False):
    connection = getConnection()
    with connection.cursor() as cursor:
        if not all:
            cursor.execute("select comment_id, content from transcriptions where transcriber = %s and content like %s",
                       (name, '%' + text + '%'))
        else:
            cursor.execute("select comment_id, content from transcriptions where content like %s",
                       ('%' + text + '%'))
        x = [(row["comment_id"], row["content"]) for row in cursor.fetchall()]
    connection.close()
    return x

def plot_history(name, whole=False):
    connection = getConnection()
    with connection.cursor() as cursor:
        cursor.execute("select * from new_gammas where transcriber = %s", (name,))
        rows = cursor.fetchall()
    times = [row["time"] for row in rows]
    values = [row["new_gamma"] for row in rows]
    if len(values) < 2:
        return False
    plt.plot(times, values, color="black")
    first = values[0]
    last = values[-1]
    if whole or first <= 50 < last:
        plt.axhline(y=51, color="lime")
    if whole or first <= 100 < last:
        plt.axhline(y=101, color="teal")
    if whole or first <= 250 < last:
        plt.axhline(y=251, color="purple")
    if whole or first <= 500 < last:
        plt.axhline(y=501, color="gold")
    if whole or first < 1000 <= last:
        plt.axhline(y=1000, color="aqua")
    if whole or last >= 2500:
        plt.axhline(y=2500, color="deeppink")
    plt.xlabel("Time")
    plt.ylabel("Gammas")
    plt.xticks(rotation=90)
    plt.gcf().subplots_adjust(bottom=0.3)
    plt.title("Gamma history of /u/{}".format(name))
    plt.savefig("graph.png")
    plt.clf()
    connection.close()
    return "graph.png"
