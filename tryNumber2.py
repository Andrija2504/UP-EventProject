import praw
import datetime
import time
import requests
import pandas as pd

# Initialize PRAW with your Reddit application credentials
reddit = praw.Reddit(
    client_id="K-8EkFx_0WON0Q9r7HDlDQ",         # your client id
    client_secret="wbb04ad2FXNHbiU7U4P3d9S2_Kciyg",      # your client secret
    user_agent="script by /u/Purple_Unicorn252104"
)

# Access the subreddit
subreddit = reddit.subreddit('Slovenia')

posts = []

# Function to process submissions
def process_submission(submission):

    # Convert Unix timestamp to a readable date
    created_date = datetime.datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S')
    
    # Extract data from each submission
    data = {
        'title': submission.title,
        'score': submission.score,
        'id': submission.id,
        'subreddit': submission.subreddit,
        'url': submission.url,
        'created_utc': created_date,
        'num_comments': submission.num_comments,
        'selftext': submission.selftext
    }
    posts.append(data)

# Main function to fetch and process submissions
def fetch_submissions():
    one_year_ago = datetime.datetime.utcnow() - datetime.timedelta(days=365)

    for submission in subreddit.top('year', limit=None):  # You can use 'new' or 'hot' as well
        # Check if the submission is within the past year
        submission_time = datetime.datetime.utcfromtimestamp(submission.created_utc)
        if submission_time > one_year_ago:
            process_submission(submission)

fetch_submissions()

posts = pd.DataFrame(posts,columns=['title', 'score', 'id', 'subreddit', 'url', 'created_utc', 'num_comments', 'selftext'])
posts.to_csv("Top Posts.csv", index=True)