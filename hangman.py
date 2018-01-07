import pickle
import re
import random
import operator

import time

UMLAUTS = True
BACKUP_FREQ = 500

words = None


def load_dict(lang):
    global words

    try:
        words = pickle.load(open(lang + ".pickle", "rb"))
    except (OSError, IOError) as e:
        with open(lang + ".dic", "r", encoding='ISO-8859-1') as dat:
            words = set(map(
                lambda s: s[:-1] if UMLAUTS else s[:-1].replace("ß", "ss").replace("ä", "ae").replace("ö",
                                                                                                      "oe").replace(
                    "ü",
                    "ue"),
                dat.readlines()))
        dat.close()
        pickle.dump(words, open(lang + ".pickle", "wb"))


class Guesser:
    def __init__(self, lang="german"):
        load_dict(lang)
        self.already_guessed = set()

        self.wordlist = words.copy()

        self.right = 0
        self.wrong = 0
        self.last_input = ""

    def new_game(self):
        self.__init__()

    def guess(self, next_input):
        if next_input == "" and self.last_input != "":
            next_input = self.last_input
        elif self.last_input != "" and "_" in self.last_input:
            if re.fullmatch(self.last_input.replace("_", "."), next_input):
                if self.last_input == next_input:
                    self.wrong += 1
                else:
                    self.right += 1
            else:
                return None, "You cheated!"

        self.last_input = next_input

        count = dict()

        if "_" not in next_input:
            return next_input, "Got it! :+1:\nRight guesses: " + str(self.right) + "\nWrong Guesses: " + str(self.wrong)

        in_len = len(next_input)
        wordlist = set(
            w.lower() for w in self.wordlist if len(w) == in_len and re.match(next_input.replace("_", "."), w.lower()))

        removelist = set()
        for b in self.already_guessed:
            if b not in next_input:
                for word in wordlist:
                    if b in word:
                        removelist.add(word)

        wordlist = wordlist.difference(removelist)

        if len(wordlist) == 0:
            return None, "I have no idea!"

        if len(wordlist) == 1:
            return list(wordlist)[0], "I think it's " + list(wordlist)[0] + "! :sunglasses:\nRight guesses: " + str(
                self.right) + "\nWrong Guesses: " + str(self.wrong)

        for c in "abcdefghijklmnopqrstuvwxyzüöäß":
            if c not in self.already_guessed and c not in next_input:
                count[c] = 0
                for w in wordlist:
                    if c in w:
                        count[c] += 1

        sorted_guesses = sorted(count.items(), key=lambda x: x[1])

        in_all_words_index = -1

        while sorted_guesses[in_all_words_index][1] == len(wordlist):
            pattern = self.where(random.sample(wordlist, 1)[0], sorted_guesses[in_all_words_index][0])
            if all(operator.eq(pattern, self.where(w, sorted_guesses[in_all_words_index][0])) for w in wordlist):
                sorted_guesses.pop(in_all_words_index)

            in_all_words_index -= 1

        guess_index = -2
        next_guess = sorted_guesses[-1]
        while sorted_guesses[guess_index][1] == sorted_guesses[guess_index + 1][1]:
            if next_guess[0] > sorted_guesses[guess_index][0]:
                next_guess = sorted_guesses[guess_index]
            guess_index -= 1

        self.already_guessed.add(next_guess[0])
        return next_guess[0], "My guess: " + str(next_guess[0]) + ", security: " + \
               str(round((next_guess[1] / len(wordlist)) * 100, 2)) + "%"

    @staticmethod
    def where(s, b):
        return list(map(lambda x: "1" if x == b else "0", s))


class Gamemaster:
    def __init__(self):
        self.word = ""
        self.already_guessed = set()

    def new_game(self, word=None):
        if word is None:
            self.word = random.sample(words, 1)[0]
        else:
            self.word = word
        self.already_guessed = set()
        return "_" * len(self.word)

    def let_guess(self, next_guess):

        if next_guess != "":
            self.already_guessed.add(next_guess)

        concealed = self.word.lower()
        for b in "abcdefghijklmnopqrstuvwxyzüöäß":
            if b not in self.already_guessed:
                concealed = concealed.replace(b, "_")

        return concealed


class result:
    time = 0

    def __init__(self, word, right, wrong, correct, path):
        self.word = word
        self.right = right
        self.wrong = wrong
        self.correct = correct
        self.path = path

    def __str__(self):
        return "result(" + ", ".join(
            [self.word, str(self.right), str(self.wrong), str(self.correct), str(round(self.time, 2))]) + ")"


def fight(word=None, wait=0.5, out=True):
    gm = Gamemaster()
    gu = Guesser()
    path = []

    gm.new_game(word)
    last_guess = ""
    next_word = ""

    while last_guess is not None and len(last_guess) <= 1:
        next_word = gm.let_guess(last_guess)
        if out: print(next_word)
        time.sleep(wait)
        last_guess, output = gu.guess(next_word)
        if out: print(output, "\n")
        time.sleep(wait)
        path.append((next_word, last_guess, output))

    if out: print("\n" + ("Correct" if gm.word.lower() == last_guess.lower() else "Incorrect") + ", the word was:",
                  gm.word)
    if out: print("\nRight guesses: " + str(gu.right) + "\nWrong Guesses: " + str(gu.wrong))

    return result(gm.word, gu.right, gu.wrong, gm.word.lower() == last_guess.lower(), path)


def fight_forever():
    while True:
        fight()

        print("\n\nNext Game!\n\n")


def fight_statistics_all(i):
    begintime = "all_" + str(round(time.time()))
    results = []
    wlist = sorted(list(words))
    for x in range(i):
        print(x + 1, "of", i)
        timebefore = time.time()
        results.append(fight(wlist[x], wait=0, out=False))
        results[-1].time = time.time() - timebefore

        with open("logs/log_" + begintime + "_" + str(i) + ".txt", "a") as dat:
            dat.write(str(results[-1]) + "\n")
            dat.close()

        if x % BACKUP_FREQ == 0:
            pickle.dump(results,
                        open("logs/results/backup/results_" + begintime + "_" + str(i) + "_backup" + str(
                            x / BACKUP_FREQ) + ".pickle",
                             "wb"))

    calc_statistics(results, begintime, "logs/log_" + begintime + "_" + str(i) + ".txt", i)


def fight_statistics_random(i):
    begintime = "rnd_" + str(round(time.time()))
    results = []
    for x in range(i):
        print(x + 1, "of", i)
        timebefore = time.time()
        results.append(fight(wait=0, out=False))
        results[-1].time = time.time() - timebefore
        with open("logs/log_" + begintime + "_" + str(i) + ".txt", "a") as dat:
            dat.write(str(results[-1]) + "\n")
            dat.close()

        if x % BACKUP_FREQ == 0 and x != 0:
            pickle.dump(results,
                        open("logs/results/backup/results_" + begintime + "_" + str(i) + "_backup" + str(
                            x // BACKUP_FREQ) + ".pickle",
                             "wb"))

    calc_statistics(results, begintime, "logs/log_" + begintime + "_" + str(i) + ".txt", i)


def calc_statistics(results, begintime, logpath, size):
    error = False
    for r in results:
        if not r.correct:
            error = True
            print("!!!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!!")
        print(r)

    if error:
        print("!!!!! ERROR !!!!!!!")

    resultstring = ("\n\nMax. wrong:" + str(max(results, key=lambda x: x.wrong)) +
                    "\nMax. right:" + str(max(results, key=lambda x: x.right)) +
                    "\nMax. all:  " + str(max(results, key=lambda x: x.right + x.wrong)) +
                    "\n\nMin. wrong:" + str(min(results, key=lambda x: x.wrong)) +
                    "\nMin. right:" + str(min(results, key=lambda x: x.right)) +
                    "\nMin. all:  " + str(min(results, key=lambda x: x.right + x.wrong)) +
                    "\n\nAvg. wrong:" + str(sum(map(lambda x: x.wrong, results)) / len(results)) +
                    "\nAvg. right:" + str(sum(map(lambda x: x.right, results)) / len(results)) +
                    "\nAvg. all:  " + str(sum(map(lambda x: x.right + x.wrong, results)) / len(results)) +
                    "\n\nMax. time:" + str(max(results, key=lambda x: x.time)) +
                    "\nMin. time:" + str(min(results, key=lambda x: x.time)) +
                    "\nAvg. time:" + str(sum(map(lambda x: x.time, results)) / len(results)))

    with open(logpath, "a") as dat:
        dat.write(resultstring)

    print(resultstring)

    pickle.dump(results, open("logs/results/results_" + begintime + "_" + str(size) + "_done.pickle", "wb"))


def play():
    last_answer = ""
    gu = Guesser()
    while last_answer is not None and len(last_answer) < 2:
        last_answer = gu.guess(input("> "))[0]
        print("My Guess:", last_answer)


if __name__ == "__main__":
    fight("schnell")
