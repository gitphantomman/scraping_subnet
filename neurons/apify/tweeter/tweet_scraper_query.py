from neurons.apify.actors import run_actor, ActorConfig


class TweetScraperQuery:
    """
    A class designed to scrape tweets based on specific search queries using the Apify platform.

    Attributes:
        actor_config (ActorConfig): Configuration settings specific to the Apify actor.
    """

    def __init__(self, actor_config: ActorConfig):
        """
        Initialize the TweetScraperQuery with the provided actor configuration.

        Args:
            actor_config (ActorConfig): Configuration settings specific to the Apify actor.
        """
        self.actor_config = actor_config

    def execute(self, search_queries: list = ["bittensor"], limit_number: int = 15) -> list:
        """
        Execute the tweet scraping process using the specified search queries.

        Args:
            search_queries (list, optional): A list of search terms to be queried. Defaults to ["bittensor"].

        Returns:
            list: A list of scraped tweet data.
        """
        run_input = {
            "searchQueries": search_queries,
            "tweetsDesired": limit_number,
            "includeUserId": True,
            "includeUserInfo": True,
            "minReplies": 0,
            "minRetweets": 0,
            "minLikes": 0,
            "fromTheseAccounts": [],
            "toTheseAccounts": [],
            "mentioningTheseAccounts": [],
            "nativeRetweets": False,
            "media": False,
            "images": False,
            "videos": False,
            "news": False,
            "verified": False,
            "nativeVideo": False,
            "replies": False,
            "links": False,
            "safe": False,
            "quote": False,
            "proVideo": False,
            "excludeNativeRetweets": False,
            "excludeMedia": False,
            "excludeImages": False,
            "excludeVideos": False,
            "excludeNews": False,
            "excludeVerified": False,
            "excludeNativeVideo": False,
            "excludeReplies": False,
            "excludeLinks": False,
            "excludeSafe": False,
            "excludeQuote": False,
            "excludeProVideo": False,
            "language": "any",
            "proxyConfig": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
            }
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
        return input


if __name__ == '__main__':
    # Define the Apify actor configuration
    _config = ActorConfig("u6ppkMWAx2E2MpEuF")

    # Initialize the tweet scraper query mechanism with the actor configuration
    query = TweetScraperQuery(actor_config=_config)

    # Execute the scraper for the "bitcoin" search term
    data_set = query.execute(search_queries=["bitcoin"])

    # Output the scraped data
    for item in data_set:
        print(item)
