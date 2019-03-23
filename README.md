# ColdWords

This is a followup to a blog post I made analyzing vocabulary richness.

https://seisvelas.blogspot.com/2019/03/literal-communism-ruined-my-reddit-api.html

Upon further investigation, much of my original findings are incorrect. This new code intends to support a new blog post correcting my original results.

## scrape_posts.py

Scrapes Reddit for subreddits related to various ideologies and uploads the text to a database

## analyze_vocab.rkt

Loads comments and calculates type/token ratio (adjusted for length bias in conventional TTR)

## todo: visualize results of Racket code's TTR

Unsure of whether I want to load the results into a SQL VIEW and visualize with Mode (which I love), versus generating the charts programmatically in Racket/Plot or Python/Seaborn.
