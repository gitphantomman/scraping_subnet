import tweepy
# from tweepy import streaming
import os
from dotenv import load_dotenv
import time
import requests

from local_db.twitter_db import store_data
load_dotenv()

bearer_token = os.getenv("BEARER_TOKEN")


def scrapTwitter(max_limit = 100, key = "bittensor"):
    url = f"https://api.twitter.com/2/tweets/search/recent?query={key}&tweet.fields=created_at&max_results={max_limit}"
    payload = {}
    headers = {
        'Authorization': f'Bearer {bearer_token}',
        }
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        returnData = response.json()['data']
        for twitterPost in returnData:
            # print(twitterPost)
            store_data(twitterPost)
    except Exception as e:
        print(e)

def continuous_scrape(interval=16):
    while True:
        try:
            scrapTwitter()
            print("Scraping done. Waiting for the next round...")
            time.sleep(interval)
        except Exception as e:
            print(f"Error occurred: {e}")
            time.sleep(16) # Wait for 30s before trying again

if __name__ == "__main__":
    continuous_scrape()





