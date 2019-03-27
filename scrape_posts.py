import requests
import json
import re
from sqlalchemy import String, Table, Column, create_engine, MetaData
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.types import DateTime
from sqlalchemy.sql import func
import os

# Todo: generate this object from ideologies table in db
IDEOLOGIES = {"capitalism": ["libertarian", "GoldandBlack", "AnCap101"],
              "communism": ["communism", "communism101"]}
REDDIT_URL = "https://www.reddit.com"
FAKE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'From': 'user@domain.tld'
}

meta = MetaData()

comments_table = Table('comments', meta,
                       Column('id', String(collation='utf8')),
                       Column('comment', String(collation='utf8')),
                       Column('createdat', DateTime),
                       Column('subreddit', String(collation='utf8')))


user = os.environ("USER")
password = os.environ("PASS")
host = os.environ("HOST")
db = os.environ("DB")


def upload(comments, ideology, subreddit):
    engine = create_engine('postgresql://%s:%s@%s:5432/%s' %
                           (user, password, host, db))
    c = engine.connect()
    trans = c.begin()

    for comment in comments:
        insertion = insert(comments_table).values(id=comment["id"],
                                                  subreddit=subreddit,
                                                  comment=comment["text"],
                                                  createdat=func.now())

        insertion = insertion.on_conflict_do_nothing(index_elements=['id'])

        c.execute(insertion)

    trans.commit()
    c.close()


def letters_only(string):
    return re.sub(r'\W+', '', string)


# TODO: Handle API errors (eg 403 quarantine Reddit error)
def get_comments(sub):
    r = requests.get("%s/r/%s.json" % (REDDIT_URL, sub), headers=FAKE_HEADERS)
    print(sub)

    posts = json.loads(r.text)["data"]["children"]
    comments = []

    for p in posts:
        comment = {}
        comment["id"] = p["data"]["id"]
        comment["text"] = p["data"]["selftext"]
        comments.append(comment)

    res = []

    for comment in comments:
        formatted_comment = []

        for word in comment["text"].split():
            if word != '' and 'http' not in word:
                formatted_comment.append(letters_only(word))

        comment["text"] = " ".join(formatted_comment)
        if comment["text"] != "":
            res.append(comment)

    return res


scores = {}

for ideology in IDEOLOGIES:
    for sub in IDEOLOGIES[ideology]:
        comments = get_comments(sub)
        upload(comments, ideology, sub)
