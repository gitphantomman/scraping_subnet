import logging
from neurons.apify.actors import run_actor, ActorConfig

# Setting up logger for debugging and information purposes
logger = logging.getLogger(__name__)

class TweetFlushQuery:
    """
    A class designed to flush tweets based on specific search queries using the Apify platform.

    Attributes:
        actor_config (ActorConfig): Configuration settings specific to the Apify actor.
    """

    def __init__(self, actor_config: ActorConfig):
        """
        Initialize the TweetFlushQuery with the provided actor configuration.

        Args:
            actor_config (ActorConfig): Configuration settings specific to the Apify actor.
        """
        self.actor_config = actor_config

    def execute(self, search_queries: list = ["bittensor"], limit_number: int = 15) -> list:
        """
        Execute the tweet flushing process using the specified search queries.

        Args:
            search_queries (list, optional): A list of search terms to be queried. Defaults to ["bittensor"].

        Returns:
            list: A list of flushed tweet data.
        """
        print(search_queries, limit_number)
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
        filtered_input = [{'id': item['tweet_id'], 'url': item['url'], 'text': item['text'], 'likes': item['likes'], 'images': item['images'], 'timestamp': item['timestamp']} for item in input]
        return filtered_input


if __name__ == '__main__':
    # Define the Apify actor configuration
    _config = ActorConfig("wHMoznVs94gOcxcZl")
    # _config.api_key = "apify_api_PWSZ5jVZhtpANm6hPDVTFdPja4Gnqc4kfdd3"  # Caution: Avoid hardcoding API keys!
    # _config.actor_id = "wHMoznVs94gOcxcZl"

    # Initialize the tweet flush query mechanism with the actor configuration
    query = TweetFlushQuery(actor_config=_config)

    # Execute the flush for the "bitcoin" search term
    data_set = query.execute(search_queries=["bitcoin"])

    # Output the flushed data
    for item in data_set:
        print(item)
