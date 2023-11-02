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
            "excludeImages": false,
            "excludeLinks": false,
            "excludeMedia": false,
            "excludeNativeRetweets": false,
            "excludeNativeVideo": false,
            "excludeNews": false,
            "excludeProVideo": false,
            "excludeQuote": false,
            "excludeReplies": false,
            "excludeSafe": false,
            "excludeVerified": false,
            "excludeVideos": false,
            "images": false,
            "includeUserId": true,
            "includeUserInfo": true,
            "language": "any",
            "links": false,
            "media": false,
            "nativeRetweets": false,
            "nativeVideo": false,
            "news": false,
            "proVideo": false,
            "proxyConfig": {
                "useApifyProxy": true,
                "apifyProxyGroups": [
                    "RESIDENTIAL"
                ]
            },
            "quote": false,
            "replies": false,
            "safe": false,
            "searchQueries": search_queries,
            "tweetsDesired": 10,
            "verified": false,
            "videos": false
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
    _config = ActorConfig("2s3kSMq7tpuC3bI6M")

    # Initialize the tweet scraper query mechanism with the actor configuration
    query = TweetScraperQuery(actor_config=_config)

    # Execute the scraper for the "bitcoin" search term
    data_set = query.execute(search_queries=["bitcoin"])

    # Output the scraped data
    for item in data_set:
        print(item)
