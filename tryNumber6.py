import praw
import time
from datetime import datetime, timedelta, timezone
import pandas as pd
import requests

reddit = praw.Reddit(
    client_id="4qVk5Cs-8EKlVR1U40beyw",         # your client id
    client_secret="i2QrEIq6IXeiF-v51nqwjNYas6lXcw",      # your client secret
    user_agent="script by /u/AndrijaP2104"
)

# Choose the subreddit
subreddit = reddit.subreddit("Slovenia")

def fetch_submissions(subreddit, after, before, limit=1000):
    url = f'https://api.pushshift.io/reddit/search/submission/'
    params = {
        'subreddit': subreddit,
        'size': limit,
        'after': after,
        'before': before
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()['data']
    else:
        return []

# Example usage
subreddit = 'Slovenia'
after = '1420070400'  # January 1, 2015, in Unix Time
before = '1640995200' # January 1, 2022, in Unix Time

submissions = fetch_submissions(subreddit, after, before)
for submission in submissions:
    print(submission['title'])
    time.sleep(1)  # Sleep to avoid hitting rate limits

# # Simple keyword search
# query = "Ljubljana OR Bled OR Triglav"  # Example keywords

# print(f"Searching for posts with keywords: {query}")

# for submission in subreddit.search(query, sort='new', limit=100):
#     print(f"Title: {submission.title}, Date: {datetime.utcfromtimestamp(submission.created_utc)}")

# # Define the overall time range
# start_date = datetime(2015, 1, 1)
# end_date = datetime(2024, 1, 1)

# # Define the duration of each time segment (e.g., 1 week)
# segment_duration = timedelta(weeks=1)

# def to_utc_timestamp(dt):
#    return int(dt.replace(tzinfo=timezone.utc).timestamp())

# while start_date < end_date:
#     # Calculate the end of the current segment
#     segment_end = min(start_date + segment_duration, end_date)

#     # Convert dates to timestamps for Reddit search
#     start_timestamp = to_utc_timestamp(start_date)
#     end_timestamp = to_utc_timestamp(segment_end)

#     # Search query for this time segment
#     query = f'timestamp:{start_timestamp}..{end_timestamp}'
#     print(f"Fetching posts from {start_date} to {segment_end}")

#     # Fetch posts in the current time segment
#     for submission in subreddit.search(query, sort='new', syntax='cloudsearch', limit=1000):
#         print(f"Title: {submission.title}, Date: {datetime.utcfromtimestamp(submission.created_utc)}")

#     # Move to the next segment
#     start_date = segment_end

#     # Optional: sleep between requests to avoid hitting rate limits
#     time.sleep(1)