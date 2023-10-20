"""
The MIT License (MIT)
Copyright © 2023 Chris Wilson

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the “Software”), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of
the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import os
import random
from dotenv import load_dotenv
from os.path import exists
import time
import requests

from local_db.twitter_db import store_data
from os.path import exists

load_dotenv()


class TwitterConfig:
    """Configuration class to hold basic twitter and scraper configurations"""
    # The Twitter API bearer token. Default is None
    bearer: str = None
    # Should the script be a single run only. Default is False
    single: bool = False
    # Number of tweets to get per single request. Default is 100
    limit: int = 100
    # How many seconds to wait before scraping again. Default is 16
    sleep_interval: int = 16
    # Maximum requests for given bearer token. Default is 10 000
    max_requests: int = 10000

    def __init__(self, limit=100):
        self.bearer = os.getenv("BEARER_TOKEN")
        self.single = True if os.getenv("SINGLE_RUN") is not None else False
        self.limit = limit

    def get_token(self):
        return self.bearer

    def get_limit(self):
        return self.limit

    def is_repeatable(self):
        return self.single is None


def scrapTwitter(config: TwitterConfig, key="tao"):
    """
    Function to scrape recent tweets based on a keyword.

    Args:
        config (TwitterConfig): Twitter configuration
        key (str): Keyword to search in tweets. Default is 'bittensor'.

    Returns:
        None
    """
    print(f"Scraping twitter for keyword: {key}, max items: {config.get_limit()}")
    # Construct the URL for the Twitter API
    url = f"https://api.twitter.com/2/tweets/search/recent?query={key}&tweet.fields=created_at&max_results={config.get_limit()}"
    payload = {}
    headers = {
        'Authorization': f'Bearer {config.get_token()}',
    }
    try:
        # Send a GET request to the Twitter API
        response = requests.request("GET", url, headers=headers, data=payload)
        # Parse the JSON response
        returnData = response.json()['data']
        if returnData.__len__() == 0:
            # If no tweets are found, return
            print("No tweets found.")
            return
        for twitterPost in returnData:
            # Store each tweet into the database
            store_data(twitterPost)
    except Exception as e:
        print('Invalid Key')


def random_line(afile="keywords.txt"):
    if not exists(afile):
        print(f"Keyword file not found at location: {afile}")
        quit()
    lines = open(afile).read().splitlines()
    return random.choice(lines)


def continuous_scrape(interval=16):
    """
    Function to continuously scrape tweets at a specified interval.

    Args:
        interval (int): Time interval (in seconds) between each scrape. Default is 16 seconds.

    Returns:
        None
    """
    while True:
        try:
            randomKey = random_line()
            # Scrape tweets
            scrapTwitter(key=randomKey)
            print("Scraping done. Waiting for the next round...")
            # Wait for the specified interval before the next round
            time.sleep(interval)
        except Exception as e:
            print(f"Error occurred: {e}")
            time.sleep(16)  # Wait for 30s before trying again


if __name__ == "__main__":
    config = TwitterConfig(12)
    # Start the continuous scraping when the script is run directly
    if config.is_repeatable():
        continuous_scrape()
    else:
        print(f"Executing single twitter scrap.")
