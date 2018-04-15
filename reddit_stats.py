import praw
import time

import passwords_and_tokens
import pymysql

reddit = praw.Reddit(client_id=passwords_and_tokens.reddit_id, client_secret=passwords_and_tokens.reddit_token,
                     user_agent="Lornebot 0.0.1")

connection = pymysql.connect(host="localhost",
                             user=passwords_and_tokens.sql_user,
                             password=passwords_and_tokens.sql_password,
                             db="torstats",
                             charset="utf8mb4",
                             cursorclass=pymysql.cursors.DictCursor,
                             port=3306)

tor = reddit.subreddit("TranscribersOfReddit")


def trans_check(st):
    return ("human" in st and
            "content" in st and
            "volunteer" in st and
            "transcriber" in st and
            "r/TranscribersOfReddit/wiki/index" in st)


def analyze_user(usr, limit=1000, ignore_last=False):
    print("Fetching stats for /u/" + usr)
    output = ""
    with connection.cursor() as cursor:

        cursor.execute("SELECT * FROM transcribers WHERE name = %s;", (usr,))
        if cursor.rowcount == 0:
            print("New user:", usr)
            output += "New user: " + usr + "\n"
            new_name = True
            cursor.execute("INSERT INTO transcribers (name) VALUES (%s)", (usr,))
        else:
            new_name = False
            row = cursor.fetchone()
            # Invalid users don't cost much time
            #if row["valid"] == False:
            #    print("User is invalid")
            #    output += "User " + usr + " is invalid!\n"
            #    return output
        try:
            u = reddit.redditor(usr)
            try:
                first_comment = next(u.comments.new(limit=1))
            except StopIteration:
                print("No comments")
                return
            if (not new_name and not ignore_last and row["last_checked_comment"] is not None
                    and first_comment == row["last_checked_comment"]):
                print("No new comments")
                update_gamma(row["reference_comment"], new_name, row["official_gamma_count"], usr)
                connection.commit()
                return
            print("Getting 10 comments")
            comments = list(u.comments.new(limit=10))
            if (not new_name and not ignore_last and not limit <= 10 and row["last_checked_comment"] is not None and
                    row["last_checked_comment"] in map(lambda c: c.id, comments)):
                print("Last checked in last 10 comments")
            else:
                print("Getting", limit, "comments")
                comments = list(u.comments.new(limit=limit))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            print("Exception", e, "Setting", usr, "to invalid")
            output += "Exception " + str(e) + ": Setting " + usr + " to invalid"
            cursor.execute("UPDATE transcribers SET valid = FALSE WHERE name = %s", (usr,))
            connection.commit()
            return output

        if len(comments) > 0:
            cursor.execute("UPDATE transcribers SET last_checked_comment = %s, valid = TRUE WHERE name = %s",
                           (comments[0].id, usr))

        reference_comment = None if new_name else row["reference_comment"]

        print("Reading", len(comments), "comments:")
        i = 0

        for com in comments:
            i += 1
            if i % 50 == 0:
                print(i, end="")
            elif i % 10 == 0:
                print(".", end="")
            if not new_name:
                if not ignore_last and com.id == row["last_checked_comment"]:
                    print(" Arrived at last known comment!")
                    break
            if reference_comment == None and com.subreddit == tor and com.author_flair_text is not None:
                cursor.execute("UPDATE transcribers SET reference_comment = %s WHERE name = %s", (com.id, usr))
                reference_comment = com.id
            elif trans_check(com.body):
                cursor.execute("insert ignore into transcriptions (comment_id, transcriber, content, subreddit, found) VALUES (%s, %s, %s, %s, now())",
                               (com.id, usr, com.body, com.subreddit.id))

        cursor.execute("UPDATE transcribers SET counted_comments = counted_comments + %s WHERE name = %s", (i, usr))

        print(" done")
        update_gamma(reference_comment, new_name, row["official_gamma_count"], usr)

    connection.commit()
    return output

def update_gamma(reference_comment, new_name, gamma_before, usr):
    if reference_comment is not None:
        if reddit.comment(reference_comment).author_flair_text is None:
            cursor.execute("update transcribers set reference_comment = null where name = %s", (usr,))
            print("No flair:", reference_comment)
        else:
            off_gamma = int(reddit.comment(reference_comment).author_flair_text.split(" ")[0])
            if not new_name and gamma_before is not None and gamma_before < off_gamma:
                print("New gamma: From", gamma_before, "to", off_gamma)
                cursor.execute("INSERT INTO new_gammas (transcriber, old_gamma, new_gamma, time) "
                               "VALUES (%s, %s, %s, now())", (usr, gamma_before, off_gamma))

            cursor.execute("UPDATE transcribers SET official_gamma_count = %s WHERE name = %s",
                           (off_gamma, usr))

if __name__ == "__main__":
    while True:
        connection = pymysql.connect(host="localhost",
                                     user=passwords_and_tokens.sql_user,
                                     password=passwords_and_tokens.sql_password,
                                     db="torstats",
                                     charset="utf8mb4",
                                     cursorclass=pymysql.cursors.DictCursor,
                                     port=3306)

        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM transcribers")
            for name in map(lambda x: x["name"], cursor.fetchall()):
                analyze_user(name)
        connection.close()
        print("--- Round done ---\n\n")
