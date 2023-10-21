import logging

from neurons.apify.apify import ApifyConfig, run_actor


class TweetFlushQuery:
    def __init__(self):
        self.run_input = {
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

    def execute(self, config=None):
        if config is None:
            config = ApifyConfig()
        return self.map(run_actor(config, self.run_input))

    def map(self, input):
        return input


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    _config = ApifyConfig()
    _config.api_key = "apify_api_PWSZ5jVZhtpANm6hPDVTFdPja4Gnqc4kfdd3"
    _config.actor_id = "3ZnxsHgu9XSzTgDcu"

    query = TweetFlushQuery()
    data_set = query.execute(config=_config)

    for item in data_set:
        print(item)
