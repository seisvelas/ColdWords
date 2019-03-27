import psycopg2
# todo: use environmental variables instead of importing from file
from database_credentials import user, host, password
from lexicalrichness import LexicalRichness
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set()  # only using seaborn for pretty plt styling

conn = psycopg2.connect("dbname='postgres' user='%s' host='%s' password='%s'" %
                        (user, host, password))

cur = conn.cursor()

smallest_ideology_file = open("smallest_ideology.sql", "r")
cur.execute(smallest_ideology_file.read())
smallest_ideology_file.close()

# get size of smallest array of ideological words
# for Standardized Type Token Ratio
smallest_wordlist_length = cur.fetchone()[0]

word_arrays_file = open("word_arrays.sql", "r")
cur.execute(word_arrays_file.read())
word_arrays_file.close()

scores = {}

for result in cur.fetchall():
    # each result consists of and ideology name
    # as it's first element, and an array
    # of words associated with that ideology
    # as it's second element, like so:

    # ("communism", ["lots", "of", "communist", "words"])

    ideology = result[0]
    # only get up to smallest_wordlist_length for STTR formula
    words = result[1][:smallest_wordlist_length]

    words_big_string = " ".join(words)
    scores[ideology] = LexicalRichness(words_big_string).ttr


# Create chart save to disk

# Michael me va a regañar por abusar los comprehensions
# se lo juro que son apropriados aquí
x_names = [ideology.capitalize() for ideology in scores]
y_values = [score for ideology, score in scores.items()]
y_pos = np.arange(len(x_names))
# plt.style.use('dark_background')
plt.bar(y_pos, y_values, align='center', color="#330033", alpha=0.7)
plt.ylim(bottom=.27, top=.285)
plt.xticks(y_pos, x_names)
plt.ylabel('Type Token Ratio')
plt.title('Lexical Richness by Ideology')

plt.savefig("barchart.png")
