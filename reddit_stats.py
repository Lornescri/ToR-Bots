import praw
import pickle
import passwords_and_tokens

reddit = praw.Reddit(client_id=passwords_and_tokens.reddit_id, client_secret=passwords_and_tokens.reddit_token,
                     user_agent="Lornebot 0.0.1")

tor = reddit.subreddit("TranscribersOfReddit")

try:
    buffer = pickle.load(open("redditors.pickle", "rb"))
except (OSError, IOError) as e:
    buffer = dict()

blacklist = set()

def trans_check(st):
    return ("human" in st and
            "content" in st and
            "volunteer" in st and
            "transcriber" in st and
            "r/TranscribersOfReddit/wiki/index" in st)


def get_flair_count(usr, limit):
    global blacklist
    global buffer

    if usr in blacklist:
        #print(usr, "is blacklisted for unexistment.")
        return -1
    if usr in buffer:
        try:
            #print("Using buffer for", usr)
            return int(reddit.comment(buffer[usr]).author_flair_text.split(" ")[0])
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            print("!!!!!!!!!!! Error in buffer with", usr)
            del buffer[usr]

    try:
        for c in reddit.redditor(usr).comments.new(limit=limit):
            if c.subreddit == tor:
                buffer[usr] = c.id
                pickle.dump(buffer, open("redditors.pickle", "wb"))
                return int(c.author_flair_text.split(" ")[0])

    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as e:
        #print(usr, "doesn't exist.")
        blacklist.add(usr)
        return -1

    #print(usr, "has no transcripts.")
    return -1

def last_trans(usr):
    print("Fetching stats for /u/" + usr)
    try:
        u = reddit.redditor(usr)
        comments = list(u.comments.new(limit=10))
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception:
        return "/u/" + usr + " is no Redditor, sorry"

    tr = list(filter(lambda x: trans_check(x.body), comments))

    if len(tr) == 0:
        return "No transcription found"
    else:
        return tr[0].permalink

def stats(usr):
    print("Fetching stats for /u/" + usr)
    try:
        u = reddit.redditor(usr)
        comments = list(u.comments.new(limit=None))
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception:
        return "/u/" + usr + " is no Redditor, sorry"

    tr = list(filter(lambda x: trans_check(x.body), comments))

    if len(tr) == 0:
        return "I see no Transcriptions from /u/" + usr

    ret = "\n\n**Number of comments (max. 1000)**: " + str(len(comments))
    ret += "\n**Number of transcriptions**: " + str(len(tr))
    f_c = get_flair_count(usr, 100)
    if f_c != -1:
        ret += "\n**Official Γ count**: " + str(f_c)
    ret += "\n**Total chars in transcriptions**: " + str(sum(map(lambda x: len(x.body), tr)))
    ret += "\n**Chars per transcription**: " + str(round(sum(map(lambda x: len(x.body), tr)) / len(tr), 2))
    ret += "\n**Total chars without footer**: " + str(sum(map(lambda x: len(x.body) - 280, tr)))
    ret += "\n**Chars per Transcription without footer**: " + str(
        round(sum(map(lambda x: len(x.body) - 280, tr)) / len(tr), 2))
    ret += "\n\nUpvotes on transcriptions: " + str(sum(map(lambda x: x.score, tr)))
    ret += "\nAvg. Upvotes per transcription: " +str(round(sum(map(lambda x: x.score, tr))/len(tr)))

    return ret

def goodbad(name):
    print("Fetching goodbad for /u/" + name)
    try:
        u = reddit.redditor(name)
        comments = list(u.comments.new(limit=None))
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception:
        return "/u/" + name + " is no Redditor, sorry"

    tr = list(filter(lambda x: trans_check(x.body), comments))

    if len(tr) == 0:
        return "No transcription found"

    gb = 0
    bb = 0
    gh = 0
    bh = 0

    for t in tr:
        try:
            t.refresh()
        except:
            pass
        for r in list(t.replies):
            rep = r.body.lower()
            if "good bot" in rep:
                gb += 1
            if "bad bot" in rep:
                bb += 1
            if "good human" in rep and "I am a bot and" not in rep:
                gh += 1
            if "bad human" in rep:
                bh += 1
    
    return "Results for *" + name + "*\n**Good bot**: " + str(gb) + "\n**Bad bot**: " + str(bb) + "\n**Good human**: " + str(gh) + "\n**Bad human**: " + str(bh)

if __name__ == "__main__":
    print(stats("Lornescri"))
    print(stats("Lornedon"))
    print(stats("udfgaszbudlfczdufgelnudfglo"))
