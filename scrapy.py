# import praw

# # Your Reddit API credentials
# client_id = 'K-8EkFx_0WON0Q9r7HDlDQ'
# client_secret = 'wbb04ad2FXNHbiU7U4P3d9S2_Kciyg'
# user_agent = 'script by /u/Purple_Unicorn252104'

# # Initialize PRAW with your credentials
# reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)

# # Keywords to search for in posts
# keywords = ['koper', 'ljubljana', 'maribor']

# # Access the subreddit
# subreddit = reddit.subreddit('Slovenia')

# # Fetch the top 10 posts
# for post in subreddit.hot(limit=max):
#     # Combine the title and selftext into one string for keyword checking
#     content = post.title.lower() + ' ' + post.selftext.lower()
#     if any(keyword in content for keyword in keywords):
#         print(f"Title: {post.title}")
#         print(f"Selftext: {post.selftext[:300]}")  # Prints first 300 characters of selftext
#         print(f"URL: {post.url}\n")

import praw
import re
import time
import datetime

def get_unix_timestamp(year, month, day):
    """ Helper function to get Unix timestamp for a given date. """
    return int(time.mktime(datetime.datetime(year, month, day, 0, 0).timetuple()))

# Initialize PRAW with your client credentials
reddit = praw.Reddit(client_id='K-8EkFx_0WON0Q9r7HDlDQ',
                        client_secret='wbb04ad2FXNHbiU7U4P3d9S2_Kciyg',
                        user_agent='script by /u/Purple_Unicorn252104')

subreddit = reddit.subreddit("Slovenia")

# Keywords
primary_keyword = r"\bEvent\b"
secondary_keywords = [r"\bSlovenia\b", r"\bKoper\b", r"\bPortoroz\b"]

# Define the date ranges
today = datetime.date.today()
first = today.replace(day=1)
last_month = first - datetime.timedelta(days=1)
last_month_start = last_month.replace(day=1)

# Calculate the periods
periods = [
    (last_month_start, last_month_start + datetime.timedelta(days=9)),
    (last_month_start + datetime.timedelta(days=10), last_month_start + datetime.timedelta(days=19)),
    (last_month_start + datetime.timedelta(days=20), last_month)
]

# Function to filter posts by date
def is_post_in_date_range(post, start_date, end_date):
    post_date = datetime.datetime.utcfromtimestamp(post.created_utc).date()
    return start_date <= post_date <= end_date

# Function to check for keywords
def has_keywords(title, text):
    if re.search(primary_keyword, title, re.IGNORECASE) or re.search(primary_keyword, text, re.IGNORECASE):
        return any(re.search(keyword, title, re.IGNORECASE) or re.search(keyword, text, re.IGNORECASE) for keyword in secondary_keywords)
    return False

# Fetch and filter posts
for start_date, end_date in periods:
    for submission in subreddit.new(limit=1000):  # Adjust the limit as needed
        if is_post_in_date_range(submission, start_date, end_date) and has_keywords(submission.title, submission.selftext):
            print(f"Title: {submission.title}, Date: {datetime.datetime.utcfromtimestamp(submission.created_utc)}")

# Note: This script may not cover all posts due to Reddit's limitations on the number of retrievable posts.
# Note: Reddit's search may not return all posts within the time range due to internal limitations.

# for submission in subreddit.new(limit=None):  # You can set a limit or use None for as many as possible
#     # Check if the primary keyword is in the title or description
#     print(i)
#     i += 1
#     if re.search(primary_keyword, submission.title, re.IGNORECASE) or re.search(primary_keyword, submission.selftext, re.IGNORECASE):
#         # Check for any of the secondary keywords
#         if any(re.search(keyword, submission.title, re.IGNORECASE) or re.search(keyword, submission.selftext, re.IGNORECASE) for keyword in secondary_keywords):
#             # Print or process the submission
#             print(f"Title: {submission.title}")
#             print(f"Description: {submission.selftext}\n")

    # Break the loop after fetching a certain number of posts (e.g., 100000)
    # ...

# Note: Be mindful of Reddit's API rate limits

# def fetch_posts(subreddit_name, keyword_list, total_limit=100000, batch_size=1000):
#     reddit = praw.Reddit(client_id='K-8EkFx_0WON0Q9r7HDlDQ',
#                          client_secret='wbb04ad2FXNHbiU7U4P3d9S2_Kciyg',
#                          user_agent='script by /u/Purple_Unicorn252104')

#     subreddit = reddit.subreddit(subreddit_name)

#     matching_posts = []
#     fetched_posts = 0
#     after = None

#     while len(matching_posts) < total_limit:
#         # Fetch a batch of posts
#         new_posts = list(subreddit.new(limit=batch_size, params={'after': after}))
        
#         if not new_posts:
#             print("No more new posts were returned from the API.")
#             break

#         for submission in new_posts:
#             # Check if the submission title or selftext contains any of the keywords
#             if any(keyword.lower() in (submission.title + ' ' + submission.selftext).lower() for keyword in keyword_list):
#                 matching_posts.append(submission)
#                 print(f"Matching post found: {submission.title}")

#         # Update the 'after' parameter to the ID of the last post in the batch
#         after = new_posts[-1].fullname
#         fetched_posts += len(new_posts)

#         # Print progress
#         print(f"Fetched {fetched_posts} posts so far. Matching posts: {len(matching_posts)}.")

#         # Sleep to respect Reddit's rate limits
#         time.sleep(1)

#         # Break if we've reached the total limit
#         if len(matching_posts) >= total_limit:
#             break

#     print(f"\nFinished fetching posts. Total matching posts fetched: {len(matching_posts)}")
#     return matching_posts

# # Example usage
# posts = fetch_posts('Slovenia', ['koper', 'event', 'dogadjaj', 'tourism', 'turizam'], total_limit=100000000, batch_size=1000)

# for item in posts:
#     print(item.url)