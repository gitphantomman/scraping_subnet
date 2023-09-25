import os
from dotenv import load_dotenv
import praw
import time
from local_db.db import store_data
load_dotenv()


client_id = os.getenv("CLIENT_ID")
# Create reddit instance with credentials from .env file
reddit = praw.Reddit(
    client_id = os.getenv("CLIENT_ID"),
    client_secret = os.getenv("CLIENT_SECRET"),
    password = os.getenv("REDDIT_PASSWORD"),
    user_agent = os.getenv("USER_AGENT"),
    username = os.getenv("REDDIT_USERNAME")
)

# Main scraping function from reddit
def scrape_reddit(subreddit_name='all', limit = 100):
    subreddit = reddit.subreddit(subreddit_name)
    for submission in subreddit.new(limit=limit):
        store_data(submission)
    print("Remaining Requests:", reddit.auth.limits['remaining'])
    print("Rate Limit Resets At:", reddit.auth.limits['reset_timestamp'])

# ! Scrap 100 posts per 30s
def continuous_scrape(interval=30):
    while True:
        try:
            scrape_reddit()
            print("Scraping done. Waiting for the next round...")
            time.sleep(interval)
        except Exception as e:
            print(f"Error occurred: {e}")
            time.sleep(30) # Wait for 30s before trying again

if __name__ == "__main__":
    continuous_scrape()