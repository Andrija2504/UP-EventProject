import praw
import time
from datetime import datetime, timedelta, timezone
import pandas as pd

reddit = praw.Reddit(
    client_id="4qVk5Cs-8EKlVR1U40beyw",         # your client id
    client_secret="i2QrEIq6IXeiF-v51nqwjNYas6lXcw",      # your client secret
    user_agent="script by /u/AndrijaP2104"
)

# Choose the subreddit
subreddit = reddit.subreddit("Slovenia")

# def to_utc_timestamp(dt):
#    return int(dt.replace(tzinfo=timezone.utc).timestamp())

# pause_duration = 60 * 60  # e.g., 1 hour
# end_time = datetime.utcnow()  # Current time
# start_time = end_time.replace(year=end_time.year - 1)  # One year ago

# while start_time < end_time:
#     start_timestamp = to_utc_timestamp(start_time)
#     end_timestamp = to_utc_timestamp(end_time)

#     query = f'timestamp:{start_timestamp}..{end_timestamp}'
#     submissions = list(subreddit.search(query, sort='new', syntax='cloudsearch', limit=1000))
#     print(submissions)
#     print(start_timestamp, " ", end_timestamp)
#     if submissions:
#         # Process submissions here
#         for submission in submissions:
#             print(submission.title)

#         # Update start_time to the timestamp of the oldest post in the batch
#         start_time = datetime.utcfromtimestamp(submissions[-1].created_utc)

#     # Pause before next fetch
#     time.sleep(pause_duration)

#     # Update end_time for the next iteration
#     end_time = datetime.utcnow()

# Define your time range here
# start_time = datetime(2024, 1, 4)  # for example, starting from January 1, 2023
# end_time = datetime(2024, 1, 6)    # ending on January 2, 2023

# # Convert to timestamps
# start_timestamp = to_utc_timestamp(start_time)
# end_timestamp = to_utc_timestamp(end_time)

# query = f'timestamp:{start_timestamp}..{end_timestamp}'
# limit = 1000  # Max limit per query

# for submission in subreddit.search(query, sort='new', syntax='cloudsearch', limit=limit):
#     print(submission.title)

additional_keywords = ['what', 'where', 'who', 'how', 'when', 'do', 'should', 'did', 
                       'was', 'were', 'will', 'have', '?', "has", "had", "would", "whose", 
                       "kam", "od kod", "s kom", "Čigav", "Čemu", "na kakšen način" "do kdaj", "od kdaj",
                       "kaj", "kdo", "kje", "kdaj", "zakaj", 'kako', 'kateri', 'katera', 'katero',
                       'koliko', 'koper', 'event', 'dogadjaj', 'kopar', 'tourism', 'turizem', 'tourist', 'turistov']

query = ' AND '.join(additional_keywords)  # Adjust the logic here if needed

# Scrape the titles of the top 10 hot posts
def fetch_posts(after_id=None):
    params = {'limit': 1000}
    if after_id:
        params['after'] = after_id

    return list(subreddit.new(params=params))

total_posts = 10000
fetched_posts = 0
last_post_id = None
posts1 = []

while fetched_posts < total_posts:
    posts = fetch_posts(last_post_id)
    if not posts:
        break

    for post in posts:
        post_content = post.title + " " + post.selftext
        #print(post_content)

        if any(keyword.lower() in post_content.lower()  for keyword in additional_keywords):
            created_date = datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S')
            data = {
                    'title': post.title,
                    'score': post.score,
                    'id': post.id,
                    'subreddit': str(post.subreddit),
                    'url': post.url,
                    'created_utc': created_date,
                    'num_comments': post.num_comments,
                    'selftext': post.selftext
                }
            posts1.append(data)
        #print(post.title)  # Process the post as needed
        last_post_id = post.fullname

    print(posts1)
    fetched_posts += len(posts)
    print(f"Total posts fetched: {fetched_posts}")

    # Sleep for 30 seconds if there are more posts to fetch
    if fetched_posts < total_posts:
        time.sleep(30)

print(posts1)
posts1 = pd.DataFrame(posts1,columns=['title', 'score', 'id', 'subreddit', 'url', 'created_utc', 'num_comments', 'selftext'])
posts1.to_csv("Posts2022Keywords.csv", index=True)