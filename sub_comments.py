import requests
import json
import re
from sqlalchemy import MetaData, String, Table, Column, Integer, create_engine
from mah_credentials import user, password, host  # postgresql user/pass/host


ideologies = ["capitalism", "communism"]


REDDIT_URL = "https://www.reddit.com"
FAKE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'From': 'jimmjoeJohnson@mywebsite.net'  # This is another valid field
}


meta = MetaData()

comments_table = Table('comments', meta,
                       Column('ideology', String(collation='utf8')),
                       Column('score', Integer))


def upload(scores):
    engine = create_engine('postgresql://%s:%s@%s:5432/postgres' %
                           (user, password, host))
    c = engine.connect()
    trans = c.begin()

    for i, s in scores.items():
        c.execute(comments_table.insert(), ideology=i, score=s)

    trans.commit()
    c.close()


def countWords(text):
    words = {}

    for w in text:
        if w in words:
            words[w] += 1
        else:
            words[w] = 1

    return words


def letters_only(string):
    return re.sub(r'\W+', '', string)


# TODO: Handle API errors (eg 403 quarantine Reddit error)
def comments(sub):
    r = requests.get("%s/r/%s.json" % (REDDIT_URL, sub), headers=FAKE_HEADERS)
    posts = json.loads(r.text)["data"]["children"]
    comments = [REDDIT_URL + p["data"]["selftext"] + ".json" for p in posts]

    # Remove links and non-alphabetic characters
    return [letters_only(i) for i in comments.split() if i not in ["http", '']]


scores = {}

for sub in ideologies:
    count = countWords(comments(sub))
    print(count)
    nums = [value for key, value in count.items()]
    avg = sum(nums) / len(nums)
    scores[sub] = int(sum([(1 if num >= avg else num / avg) for num in nums]))


upload(scores)
