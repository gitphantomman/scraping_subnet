import logging
from neurons.apify.apify import ApifyConfig, run_actor


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    config = ApifyConfig()
    config.api_key = "apify_api_PWSZ5jVZhtpANm6hPDVTFdPja4Gnqc4kfdd3"

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
        "max_tweets": 10,
        "only_tweets": False,
        "queries": [
            "bittensor"
        ],
        "use_experimental_scraper": False,
        "language": "any",
        "user_info": "user info and replying info",
        "max_attempts": 5
    }

    data_set = run_actor("3ZnxsHgu9XSzTgDcu", {}, config=config)

    for item in data_set:
        print(item)