import requests
import json
import re
from sqlalchemy import String, Table, Column, Integer, create_engine, MetaData
from database_credentials import user, password, host  # postgresql user/pass/host


IDEOLOGIES = ["capitalism", "communism"]
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


def count_words(text):
    print(text)
    count = {}

    for word in text:
        if word in count:
            count[word] += 1
        else:
            count[word] = 1

    return count


def letters_only(string):
    return re.sub(r'\W+', '', string)


# TODO: Handle API errors (eg 403 quarantine Reddit error)
def comments(sub):
    r = requests.get("%s/r/%s.json" % (REDDIT_URL, sub), headers=FAKE_HEADERS)
    posts = json.loads(r.text)["data"]["children"]
    comments = [REDDIT_URL + p["data"]["selftext"] + ".json" for p in posts]
    # Remove links and non-alphabetic characters
    return [letters_only(i) for i in comments if i and ('http' not in i)]


scores = {}

for sub in IDEOLOGIES:
    count = count_words(comments(sub))
    nums = [value for key, value in count.items()]
    avg = sum(nums) / len(nums)
    scores[sub] = int(sum([(1 if num >= avg else num / avg) for num in nums]))


upload(scores)
