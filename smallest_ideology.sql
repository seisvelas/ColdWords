SELECT array_length(STRING_TO_ARRAY(LOWER(STRING_AGG(c.comment, ' ')), ' '), 1) AS size
FROM public.comments c
JOIN public.ideologies i
  ON c.subreddit=ANY(i.subreddits)
GROUP BY i.ideology
ORDER BY size LIMIT 1;