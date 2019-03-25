/*

Generates a row for each ideology containing
the ideology name along with an arry of
all of the words that appear in that 
ideology's subreddit posts

*/

SELECT i.ideology,
       STRING_TO_ARRAY(LOWER(STRING_AGG(c.comment, ' ')), ' ')
FROM public.comments c
JOIN public.ideologies i
  ON c.subreddit=ANY(i.subreddits)
GROUP BY i.ideology;
