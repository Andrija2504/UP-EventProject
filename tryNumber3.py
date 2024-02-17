import requests
import datetime
import praw
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
headers = {
    'User-Agent': 'script by /u/Purple_Unicorn252104'
}
# Function to process submissions

def get_pushshift_data(after, before, sub, last_id=None):
    url = f'https://api.pushshift.io/reddit/submission/search/?subreddit={sub}&after={after}&before={before}&sort_type=created_utc&sort=asc&size=1000'
    if last_id:
        url += f"&before_id={last_id}"
    r = requests.get(url, headers=headers)
    
    # Check if the response is successful
    if r.status_code != 200:
        print(f"Error: Received status code {r.status_code}")
        return []

    data = r.json()
    
    # Check if 'data' key exists in the response
    if 'data' not in data:
        print("Error: 'data' key not in response")
        print(data)  # Print what's actually in the response
        return []

    return data['data']

def fetch_posts(subreddit, start, end):
    chunk_size = 30  # days
    while start < end:
        new_start = start + chunk_size * 86400  # Start of next chunk
        submissions = get_pushshift_data(start, min(new_start, end), subreddit)
        if submissions:
            last_id = submissions[-1]['id']
            process_submissions([submission['id'] for submission in submissions])
            start = new_start
        else:
            break
        time.sleep(1)  # Respectful delay between requests

def process_submissions(submission_ids):
    for submission_id in submission_ids:
        try:
            submission = reddit.submission(id=submission_id)

            # Convert Unix timestamp to a readable date
            created_date = datetime.datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S')

            # Extract data from each submission
            data = {
                'title': submission.title,
                'score': submission.score,
                'id': submission.id,
                'subreddit': str(submission.subreddit),
                'url': submission.url,
                'created_utc': created_date,
                'num_comments': submission.num_comments,
                'selftext': submission.selftext
            }

            # You can print, save to a file, or perform other operations with 'data'
            posts.append(data)

            time.sleep(1)  # Sleep to respect Reddit API rate limits

        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(60)  # Sleep for 60 seconds on error

# Example usage
one_year_ago = int((datetime.datetime.utcnow() - datetime.timedelta(days=365)).timestamp())
now = int(datetime.datetime.utcnow().timestamp())

fetch_posts('Slovenia', one_year_ago, now)


posts = pd.DataFrame(posts,columns=['title', 'score', 'id', 'subreddit', 'url', 'created_utc', 'num_comments', 'selftext'])
posts.to_csv("Top Posts.csv", index=True)

# https://github.com/pushshift/api/blob/master/api/Submission.py
# https://brightdata.com/blog/web-data/how-to-scrape-reddit-python
# https://medium.com/geekculture/a-complete-guide-to-web-scraping-reddit-with-python-16e292317a52
