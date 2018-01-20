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


def analyze_trans(trans):
    try:
        trans.refresh()
    except Exception:
        try:
            trans.refresh()
        except Exception:
            print("Error in refresh:", trans.id)

            with connection.cursor() as cursor:
                cursor.execute("update transcriptions set good_bot = 0, bad_bot = 0, good_human = 0, bad_human = 0, "
                               "comment_count = 0, upvotes = 0, last_checked = now(), error = true where comment_id = %s",
                               (trans.id,))
                connection.commit()
            return

    replies = trans.replies
    if replies is None:
        print("No replies")
        return
    replies.replace_more(0)

    comment_count = 0
    good_bot = 0
    bad_bot = 0
    good_human = 0
    bad_human = 0

    for comment in replies:
        comment_count += 1
        content = comment.body.lower()
        if "good bot" in content:
            good_bot += 1
        if "bad bot" in content:
            bad_bot += 1
        if "good human" in content:
            good_human += 1
        if "bad human" in content:
            bad_human += 1

    print(good_bot, bad_bot, good_human, bad_human, comment_count, trans.score)

    with connection.cursor() as cursor:
        cursor.execute("update transcriptions set good_bot = %s, bad_bot = %s, good_human = %s, bad_human = %s, "
                       "comment_count = %s, upvotes = %s, last_checked = now(), error = false where comment_id = %s",
                       (good_bot, bad_bot, good_human, bad_human, comment_count, trans.score, trans.id))
    connection.commit()


if __name__ == "__main__":
    while (True):
        with connection.cursor() as cursor:
            cursor.execute("select comment_id from transcriptions where unix_timestamp(now())-unix_timestamp(found) < (24 * 60 * 60) order by last_checked asc")
            trans_list = [reddit.comment(row["comment_id"]) for row in cursor.fetchall()]
            for trans in trans_list:
                print(trans)
                analyze_trans(trans)
        time.sleep(60)
