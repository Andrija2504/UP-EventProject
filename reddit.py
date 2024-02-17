import praw
import pandas as pd
from praw.models import MoreComments
 
reddit = praw.Reddit(client_id="K-8EkFx_0WON0Q9r7HDlDQ",         # your client id
                               client_secret="wbb04ad2FXNHbiU7U4P3d9S2_Kciyg",      # your client secret
                               user_agent="script by /u/Purple_Unicorn252104")        # your user agent

posts = []
subreddit = reddit.subreddit('Slovenia')
for post in subreddit.hot(limit=10):
    posts.append([post.title, post.score, post.id, post.subreddit, post.url, post.num_comments, post.selftext, post.created])
posts = pd.DataFrame(posts,columns=['title', 'score', 'id', 'subreddit', 'url', 'num_comments', 'body', 'created'])
print(posts)