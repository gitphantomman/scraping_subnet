import os
from dotenv import load_dotenv
import praw
import time
from local_db.reddit_db import store_data

# Load environment variables from .env file
load_dotenv()

# Fetch client_id from environment variables
client_id = os.getenv("CLIENT_ID")

# Create reddit instance with credentials from .env file
# TODO: Add error handling for missing environment variables
reddit = praw.Reddit(
    client_id = os.getenv("CLIENT_ID"),
    client_secret = os.getenv("CLIENT_SECRET"),
    password = os.getenv("REDDIT_PASSWORD"),
    user_agent = os.getenv("USER_AGENT"),
    username = os.getenv("REDDIT_USERNAME")
)

# Main scraping function from reddit
# This function fetches new posts from a given subreddit
# TODO: Add error handling for invalid subreddit names
def scrape_reddit(subreddit_name='all', limit = 100):
    """Scrape the given subreddit and store the data.

    Args:
        subreddit_name (str): The name of the subreddit to scrape. Defaults to 'all'.
        limit (int): The number of posts to scrape. Defaults to 100.
    """
    subreddit = reddit.subreddit(subreddit_name)
    for submission in subreddit.new(limit=limit):
        store_data(submission)
    print("Remaining Requests:", reddit.auth.limits['remaining'])
    print("Rate Limit Resets At:", reddit.auth.limits['reset_timestamp'])

# Function to continuously scrape reddit at a given interval
# TODO: Add error handling for invalid interval values
def continuous_scrape(interval=30):
    """Continuously scrape reddit at the given interval.

    Args:
        interval (int): The interval (in seconds) at which to scrape. Defaults to 30.
    """
    while True:
        try:
            scrape_reddit()
            print("Scraping done. Waiting for the next round...")
            time.sleep(interval)
        except Exception as e:
            print(f"Error occurred: {e}")
            time.sleep(30) # Wait for 30s before trying again

# Main function to start the continuous scraping
if __name__ == "__main__":
    continuous_scrape()