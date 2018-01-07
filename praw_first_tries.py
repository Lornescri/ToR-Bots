import praw
import matplotlib as mpl
import matplotlib.pyplot as pyp
import time
import passwords_and_tokens

reddit = praw.Reddit(client_id = passwords_and_tokens.reddit_id, client_secret = passwords_and_tokens.reddit_token, user_agent = "Lornebot 0.0.1")

me = reddit.redditor("Lornescri")

comments = list(me.comments.top(limit=None))

dones = list(filter(lambda x: x.body == "done", comments))

claims = list(filter(lambda x: x.body == "claim", comments))

transcs = list(filter(lambda x: "volunteer" in x.body, comments))

def to_time(s):
    t = time.localtime(s)
    ret = t.tm_mon
    ret = ret * 100 + t.tm_mday
    ret = ret * 100 + t.tm_hour
    ret = ret * 100 + t.tm_min
    ret = ret * 100 + t.tm_sec
    return ret

times_cl = list(map(lambda x: x.created_utc, transcs))

if __name__ == "__main__":
    pyp.gcf().autofmt_xdate()
    pyp.hist(times_cl, histtype="step", cumulative=True, bins=range(round(min(times_cl)), round(max(times_cl) + 1)))

    pyp.show()