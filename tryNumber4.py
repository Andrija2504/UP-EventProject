import praw
import datetime
import time
import pandas as pd

def utc_to_datetime(utc_timestamp):
    return datetime.datetime.utcfromtimestamp(utc_timestamp)

reddit = praw.Reddit(
    client_id="K-8EkFx_0WON0Q9r7HDlDQ",         # your client id
    client_secret="wbb04ad2FXNHbiU7U4P3d9S2_Kciyg",      # your client secret
    user_agent="script by /u/Purple_Unicorn252104"
)

subreddit = reddit.subreddit('Slovenia')
main_keyword = "tourism"
additional_keywords = ['what', 'where', 'who', 'how', 'when', 'do', 'should', 'did', 
                       'was', 'were', 'will', 'have', '?', "has", "had", "would", "whose", 
                       "kam", "od kod", "s kom", "Čigav", "Čemu", "na kakšen način" "do kdaj", "od kdaj",
                       "kaj", "kdo", "kje", "kdaj", "zakaj", 'kako', 'kateri', 'katera', 'katero',
                       'koliko', 'koper', 'event', 'dogadjaj', 'kopar']
posts = []

# Define your date range
start_date = datetime.datetime(2020, 1, 1)  # Example start date: January 1, 2022
end_date = datetime.datetime(2023, 12, 31)  # Example end date: December 31, 2022

start_dates = [datetime.datetime(2022, month, 1) for month in range(1, 13)]
end_dates = [datetime.datetime(2022, month, 28) if month in [2] else 
             datetime.datetime(2022, month, 30) if month in [4, 6, 9, 11] else 
             datetime.datetime(2022, month, 31) for month in range(1, 13)]

# Function to convert UTC to a datetime object
def utc_to_datetime(utc_time):
    return datetime.datetime.utcfromtimestamp(utc_time)

# Loop through each month of 2019
for month in range(1, 13):
    start_date = datetime.datetime(2019, month, 1)
    # Handling for December (next year)
    if month == 12:
        end_date = datetime.datetime(2020, 1, 1)
    else:
        end_date = datetime.datetime(2019, month + 1, 1)

    for submission in subreddit.new(limit=None):
        post_date = utc_to_datetime(submission.created_utc)
        if start_date <= post_date < end_date:
            created_date = datetime.datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S')
            # Process the submission here
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
            posts.append(data)
            print(f"Title: {submission.title}, Date: {post_date}, URL: {submission.url}")

    print(f"Completed month: {start_date.strftime('%B %Y')}")
    time.sleep(30)  # Sleep for 30 seconds

# for i in range(0, len(start_dates)):
#     for submission in subreddit.search(main_keyword, sort='new', limit=None):
#         post_date = utc_to_datetime(submission.created_utc)
#         if start_dates[i] <= post_date <= end_dates[i]:
#             post_content = submission.title + " " + submission.selftext
#             if any(keyword.lower() in post_content.lower()  for keyword in additional_keywords):
#                 print(submission.title, post_date, submission.url, submission.selftext)

#                 # Convert Unix timestamp to a readable date
#                 created_date = datetime.datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S')

#                 # Extract data from each submission
                # data = {
                #     'title': submission.title,
                #     'score': submission.score,
                #     'id': submission.id,
                #     'subreddit': str(submission.subreddit),
                #     'url': submission.url,
                #     'created_utc': created_date,
                #     'num_comments': submission.num_comments,
                #     'selftext': submission.selftext
                # }

#                 # You can print, save to a file, or perform other operations with 'data'
#                 posts.append(data)
#     print("I sleep now")
#     time.sleep(60)  # Sleep to respect Reddit API rate limits
#     print("I am awake now")


posts = pd.DataFrame(posts,columns=['title', 'score', 'id', 'subreddit', 'url', 'created_utc', 'num_comments', 'selftext'])
posts.to_csv("Posts2022.csv", index=True)