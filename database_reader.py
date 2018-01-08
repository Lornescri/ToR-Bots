import pymysql

import passwords_and_tokens

connection = pymysql.connect(host="localhost",
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


def gammas():
    with connection.cursor() as cursor:
        cursor.execute("select name, official_gamma_count from transcribers where not official_gamma_count is null")

    return [(row["name"], row["official_gamma_count"]) for row in cursor.fetchall()]


def stats(name):
    with connection.cursor() as cursor:
        cursor.execute(
            "select official_gamma_count, counted_comments, count(comment_id) as comment_count, sum(length(content)) as total_length "
            "from transcribers left outer join transcriptions on name = transcriber where name = %s group by name",
            (name,))
        row = cursor.fetchone();

    return ("Official Γ count: {}\n"
            "Number of transcriptions I see: {}\n"
            "Total character count of transcriptions I see: {}\n"
            "*I counted {} of your total comments*".format(row["official_gamma_count"], row["comment_count"],
                                                           row["total_length"], row["counted_comments"]))





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
