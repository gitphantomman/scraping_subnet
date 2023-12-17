import logging
from neurons.apify.actors import run_actor, ActorConfig

# Setting up logger for debugging and information purposes
logger = logging.getLogger(__name__)

class TweetFlashQuery:
    """
    A class designed to query tweets based using the Tweet Flash actor on the Apify platform.

    Attributes:
        actor_config (ActorConfig): Configuration settings specific to the Apify actor.
    """

    def __init__(self):
        """
        Initialize the TweetFlashQuery.
        """
        self.actor_config = ActorConfig("wHMoznVs94gOcxcZl")
        self.actor_config.memory_mbytes = 256
        self.actor_config.timeout_secs = 30


    def searchByUrl(self, urls: list = ["https://twitter.com/elonmusk/status/1384874438472844800"]):
        """
        Search for tweets by url.
        """
        run_input = {
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
            "only_tweets": False,
            "tweet_urls": urls,
            "use_experimental_scraper": False,
            "max_tweets": 1,
            "num_threads": 5,
            "language": "any",
            "user_info": "only user info",
            "max_attempts": 5
            }
        return self.map(run_actor(self.actor_config, run_input))
    
    def execute(self, search_queries: list = ["bittensor"], limit_number: int = 15, validator_key: str = "None", validator_version: str = None, miner_uid: int = 0) -> list:
        """
        Search for tweets using search terms.

        Args:
            search_queries (list, optional): A list of search terms to be queried. Defaults to ["bittensor"].

        Returns:
            list: A list of tweets.
        """
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
            "max_tweets": limit_number,
            "only_tweets": False,
            "queries": search_queries,
            "num_threads": 1,
            "use_experimental_scraper": False,
            "language": "any",
            "user_info": "user info and replying info",
            "max_attempts": 5
        }

        return self.map(run_actor(self.actor_config, run_input))

    def map(self, input: list) -> list:
        """
        Potentially map the input data as needed. As of now, this method serves as a placeholder and simply returns the
        input data directly.

        Args:
            input (list): The data to potentially map or transform.

        Returns:
            list: The mapped or transformed data.
        """
        filtered_input = [{
            'id': item['tweet_id'], 
            'url': item['url'], 
            'text': item['text'], 
            'likes': item['likes'], 
            'images': item['images'], 
            'username': item['username'],
            'hashtags': item['tweet_hashtags'],
            'timestamp': item['timestamp']
        } for item in input]
        return filtered_input


if __name__ == '__main__':
    # Initialize the tweet query mechanism
    query = TweetFlashQuery()

    # Execute the query for the "bitcoin" search term
    data_set = query.execute(search_queries=["bitcoin"], limit_number=24)

    urls = [tweet['url'] for tweet in data_set]
    print(f"Fetched {len(urls)} urls: {urls}")

    data_set = query.searchByUrl(urls=urls)

    verified_urls = [tweet['url'] for tweet in data_set]

    print(f"Verification returned {len(verified_urls)} tweets")
    print(f"There are {len(set(verified_urls))} unique urls")

    unverified = set(urls) - set(verified_urls)

    print(f"Num unverified: {len(unverified)}: {unverified}")

    # Output the tweet data
    #for item in data_set:
    #    print(item)
