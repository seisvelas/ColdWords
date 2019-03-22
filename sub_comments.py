import requests
import json
import re
import sqlalchemy
import mah_credentials # postgresql user/pass here

meta = sqlalchemy.MetaData()

comments_table = sqlalchemy.Table('comments', meta,
    sqlalchemy.Column('ideology', sqlalchemy.String(collation='utf8')),
    sqlalchemy.Column('score', sqlalchemy.Integer)
)

def upload(scores):
    print('postgresql://%s:%s@%s:5432/postgres' % (mah_credentials.user, mah_credentials.password, mah_credentials.host))
    engine = sqlalchemy.create_engine('postgresql://%s:%s@%s:5432/postgres' % (mah_credentials.user, mah_credentials.password, mah_credentials.host))
    c = engine.connect()
    trans = c.begin()
    for i, s in scores.items():
        c.execute(comments_table.insert(),ideology=i, score=s)
    trans.commit()
    c.close()


reddit = "https://www.reddit.com"
headers_evil_FAKE = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'From': 'jimmjoeJohnson@mywebsite.net'  # This is another valid field
}

def countWords(text):
    words = {}

    for w in text:
        if w in words:
            words[w] += 1
        else:
            words[w] = 1
        
    return words

def comments(sub):

	# I am too hacky with parsing JSON / API stuff
	# how do I do this gracefully?
	
	r = requests.get("%s/r/%s.json" % (reddit, sub), headers=headers_evil_FAKE)
	subredditJSON = json.loads(r.text)["data"]["children"]
	words = [str(reddit + url["data"]["selftext"] + ".json") for url in subredditJSON]
	return countWords([i for i in [re.sub(r'\W+', '', i) for i in " ".join(words).split() if "http" not in i] if i!=''])

ideologies = ["capitalism", "communism"]

scores = {}

for sub in ideologies:
    count = comments(sub)
    print(count)
    nums = [value for key, value in count.items()]
    avg = sum(nums)/len(nums)
    scores[sub] = int(sum([(1 if num>=avg else num/avg) for num in nums]))
    
upload(scores)