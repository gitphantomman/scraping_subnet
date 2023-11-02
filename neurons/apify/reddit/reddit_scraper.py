import logging
from neurons.apify.actors import run_actor, ActorConfig

# Setting up logger for debugging and information purposes
logger = logging.getLogger(__name__)

class RedditScraper:
    """
    A class designed to scrap reddit posts based on specific search queries using the Apify platform.

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

    def searchByUrl(self, urls: list = ["https://twitter.com/elonmusk/status/1384874438472844800"]):
        """
        Execute the tweet flushing process using the specified search queries.
        """
        run_input = {
            "debugMode": False,
            "maxComments": 1,
            "maxCommunitiesCount": 1,
            "maxItems": 1,
            "maxPostCount": 1,
            "maxUserCount": 1,
            "proxy": {
                "useApifyProxy": True
            },
            "scrollTimeout": 40,
            "searchComments": False,
            "searchCommunities": False,
            "searchPosts": True,
            "searchUsers": False,
            "skipComments": False,
            "startUrls": [
                {
                "url": urls[0]
                }
            ]
            }
        return self.map(run_actor(self.actor_config, run_input))
    # ! Fix this fn
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
            "debugMode": False,
            "maxComments": 10,
            "maxCommunitiesCount": 2,
            "maxItems": 10,
            "maxPostCount": 10,
            "maxUserCount": 2,
            "proxy": {
                "useApifyProxy": True
            },
            "scrollTimeout": 40,
            "searchComments": False,
            "searchCommunities": False,
            "searchPosts": True,
            "searchUsers": False,
            "searches": search_queries,
            "skipComments": False
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
        filtered_input = [{'id': item['id'], 'url': item['url'], 'text': item['body'], 'likes': item['upVotes'], 'dataType': item['dataType'], 'timestamp': item['createdAt']} for item in input]
        return filtered_input


if __name__ == '__main__':
    # Define the Apify actor configuration
    _config = ActorConfig("FgJtjDwJCLhRH9saM")
    # _config.api_key = "apify_api_PWSZ5jVZhtpANm6hPDVTFdPja4Gnqc4kfdd3"  # Caution: Avoid hardcoding API keys!
    # _config.actor_id = "wHMoznVs94gOcxcZl"

    # Initialize the tweet flush query mechanism with the actor configuration
    query = RedditScraperLite(actor_config=_config)

    # Execute the flush for the "bitcoin" search term
    data_set = query.execute(search_queries=["bitcoin"])

    # Output the flushed data
    for item in data_set:
        print(item)
