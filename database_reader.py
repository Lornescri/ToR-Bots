import pymysql
import matplotlib, datetime
matplotlib.use("AGG")
import matplotlib.pyplot as plt

import passwords_and_tokens

connection = pymysql.connect(host=passwords_and_tokens.sql_ip,
                             user=passwords_and_tokens.sql_user,
                             password=passwords_and_tokens.sql_password,
                             db="torstats",
                             charset="utf8mb4",
                             cursorclass=pymysql.cursors.DictCursor,
                             port=3306)


def get_flair_count(reddit_name, discord_id):
    with connection.cursor() as cursor:
        cursor.execute("select * from transcribers where name = %s", (reddit_name,))
        if cursor.rowcount < 1:
            add_user(reddit_name, discord_id)
            return -1

        row = cursor.fetchone()

        if not row["valid"] or row["official_gamma_count"] is None:
            return -1

        return row["official_gamma_count"]


def all_history():
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

    return "graph.png"


def plot_history(name, whole=False):
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

    return "graph.png"


def plot_rate(name):

    with connection.cursor() as cursor:
        cursor.execute("select * from new_gammas where transcriber = %s", (name,))
        rows = cursor.fetchall()

    #print(rows[0])
    start = datetime.datetime(2017, 11, 1)
    end = datetime.datetime.now()
    step = datetime.timedelta(days=1)


    result = []
    while start < end:
        result.append(start)
        start += step

    times = result
    values = [0 for i in range(len(times))]

    
    def find_ind(times, dt):
        for i, t in enumerate(times):
            try:
                if dt >= t and times[i + 1] > dt:
                    return i
            except:
                return len(times) - 1
    for gammachange in rows:
        values[find_ind(times, gammachange["time"])] += gammachange["new_gamma"] - gammachange["old_gamma"]
    [print(times[i], values[i]) for i,v in enumerate(values) if v > 100]

    plt.plot(times, values, linewidth=0.2)


    plt.xlabel("Time")
    plt.ylabel("Gammas")
    plt.title("Gamma gain rate of /u/{}".format(name))
    plt.savefig("graph.png")
    plt.clf()

    return "graph.png"


def get_total_gammas():
    with connection.cursor() as cursor:
        cursor.execute("select sum(official_gamma_count) as gamma_count from transcribers")
        return cursor.fetchone()["gamma_count"]


def gammas():
    with connection.cursor() as cursor:
        cursor.execute("select name, official_gamma_count from transcribers where not official_gamma_count is null")

    return [(row["name"], row["official_gamma_count"]) for row in cursor.fetchall()]


def kumas():
    with connection.cursor() as cursor:
        cursor.execute("select official_gamma_count from transcribers where name = 'kumalumajuma'")

    return cursor.fetchone()["official_gamma_count"]


def stats(name):
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

    return (
        row["counted_comments"], row["official_gamma_count"], row["comment_count"], row["total_length"], upvotes,
        good_bot, bad_bot, good_human, bad_human, row["valid"])


def info():
    with connection.cursor() as cursor:
        cursor.execute("select * from info;")
        row = cursor.fetchone()

    return row["most_recent"], row["least_recent"], row["difference"], row["running"]


def all_stats():
    with connection.cursor() as cursor:
        cursor.execute(
            "select count(comment_id) as comment_count, sum(length(content)) as total_length,"
            "sum(upvotes) as upvotes, sum(good_bot) as good_bot, sum(bad_bot) as bad_bot, "
            "sum(good_human) as good_human, sum(bad_human) as bad_human from transcriptions")
        row = cursor.fetchone()

    return (row["comment_count"], row["total_length"], row["upvotes"],
            row["good_bot"], row["bad_bot"], row["good_human"], row["bad_human"])


def get_new_flairs(last_time):
    with connection.cursor() as cursor:
        cursor.execute(
            "select name, old_gamma, new_gamma, discord_id from new_gammas inner join transcribers on name = transcriber"
            " where unix_timestamp(time) > %s", (last_time,))

    return [(row["name"], row["old_gamma"], row["new_gamma"], row["discord_id"]) for row in cursor.fetchall()]


def add_user(usr, discord_id):
    with connection.cursor() as cursor:
        cursor.execute("insert ignore into transcribers (name, discord_id) values (%s, %s)", (usr, discord_id))
    connection.commit()


def get_transcriptions(name):
    with connection.cursor() as cursor:
        cursor.execute("select comment_id from transcriptions where transcriber = %s", (name,))

        return [row["comment_id"] for row in cursor.fetchall()]


def find_comments(name, text):
    with connection.cursor() as cursor:
        cursor.execute("select comment_id, content from transcriptions where transcriber = %s and content like %s",
                       (name, '%' + text + '%'))
        return [(row["comment_id"], row["content"]) for row in cursor.fetchall()]
