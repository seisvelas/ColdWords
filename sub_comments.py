import requests
import json
import re
from sqlalchemy import String, Table, Column, Integer, create_engine, MetaData
from database_credentials import user, password, host  # postgresql user/pass/host


IDEOLOGIES = {"capitalism":["the_donald", "capitalism", "libertarian"], "communism":["stalin_quotes", "communism", "communism101"]}
REDDIT_URL = "https://www.reddit.com"
FAKE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'From': 'jimmjoeJohnson@mywebsite.net'  # This is another valid field
}


meta = MetaData()

comments_table = Table('comments', meta,
                       Column('comment', String(collation='utf8')),
                       Column('created_at', Timestamp),
                       Column('subreddit', String()))


def upload(comments, ideology, subreddit):
    engine = create_engine('postgresql://%s:%s@%s:5432/postgres' %
                           (user, password, host))
    c = engine.connect()
    trans = c.begin()

    for comment in comments:
        c.execute(comments_table.upsert(), ideology=i, score=s)

    trans.commit()
    c.close()


def letters_only(string):
    return re.sub(r'\W+', '', string)


# TODO: Handle API errors (eg 403 quarantine Reddit error)
def comments(sub):
    r = requests.get("%s/r/%s.json" % (REDDIT_URL, sub), headers=FAKE_HEADERS)
    posts = json.loads(r.text)["data"]["children"]
    comments = [REDDIT_URL + p["data"]["selftext"] + ".json" for p in posts]
    # Remove links and non-alphabetic characters
    res = []
    for comment in comments:
        for word in comment.split():
            if word and 'http' not in word:
                res.append(letters_only(word))

    return res


scores = {}

for ideology  in IDEOLOGIES:
    for sub in ideology:
        comments = comments(sub)
        upload(comments, ideology, sub)
