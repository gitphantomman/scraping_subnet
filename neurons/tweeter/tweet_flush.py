from apify_client import ApifyClient
import os

from dotenv import load_dotenv
load_dotenv()
token = os.getenv("Apify_TOKEN")
# Initialize the ApifyClient with your API token
client = ApifyClient("apify_api_PWSZ5jVZhtpANm6hPDVTFdPja4Gnqc4kfdd3")

# Prepare the Actor input
def getTweets():
    run_input = {
    "collect_user_info": False,
    "detect_language": False,
    "filter:blue_verified": False,
    "filter:has_engagement": False,
    "filter:images": False,
    "filter:media": False,
    "filter:nativeretweets": False,
    "filter:quote": False,
    "filter:replies": False,
    "filter:retweets": False,
    "filter:safe": False,
    "filter:twimg": False,
    "filter:verified": False,
    "filter:videos": False,
    "max_tweets": 100,
    "only_tweets": False,
    "queries": [
        "bittensor"
    ],
    "use_experimental_scraper": False,
    "language": "any",
    "user_info": "user info and replying info",
    "max_attempts": 5
    }

    # Run the Actor and wait for it to finish
    run = client.actor("3ZnxsHgu9XSzTgDcu").call(run_input=run_input)

    # Fetch and print Actor results from the run's dataset (if there are any)
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        print(item)
