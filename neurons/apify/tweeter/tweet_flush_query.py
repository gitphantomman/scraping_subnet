import logging
from neurons.apify.actors import run_actor, ActorConfig


class TweetFlushQuery:

    def __init__(self, actor_config):
        self.actor_config = actor_config

    def execute(self, search_queries=["bittensor"]):
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
            "queries": search_queries,
            "use_experimental_scraper": False,
            "language": "any",
            "user_info": "user info and replying info",
            "max_attempts": 5
        }

        return self.map(run_actor(self.actor_config, run_input))

    def map(self, input):
        return input


if __name__ == '__main__':
    _config = ActorConfig()
    _config.api_key = "apify_api_PWSZ5jVZhtpANm6hPDVTFdPja4Gnqc4kfdd3"
    _config.actor_id = "3ZnxsHgu9XSzTgDcu"

    query = TweetFlushQuery(actor_config=_config)
    data_set = query.execute(search_queries=["bitcoin"])

    for item in data_set:
        print(item)
