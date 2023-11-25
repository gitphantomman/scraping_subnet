import logging
from datetime import datetime
from neurons.apify.actors import run_actor, ActorConfig

# Setting up logger for debugging and information purposes
logger = logging.getLogger(__name__)

class WebHarvesterTwitterScraperQuery:
    """
    A class designed to query tweets based on specific search queries using the Apify platform.

    Attributes:
        actor_config (ActorConfig): Configuration settings specific to the Apify actor.
    """

    def __init__(self):
        """
        Initialize the WebHarvesterTwitterScraperQuery.
        """
        self.actor_config = ActorConfig("VsTreSuczsXhhRIqa")

    def searchByUrl(self, urls: list = ["https://twitter.com/const_reborn/status/1725967725762134121", "https://twitter.com/opentensor/status/1713958073226649948"]):
        """
        Execute the tweet query process using the specified search queries.
        """
        run_input = {
            "includeUserInfo": False,
            "proxyConfig": {
                "useApifyProxy": True,
                "apifyProxyGroups": [
                    "RESIDENTIAL"
                ]
            },
            "startUrls": [{"url": url} for url in urls],
            "tweetsDesired": 1,
            "withReplies": True
        }
        return self.map(run_actor(self.actor_config, run_input))
    
    def execute(self, search_queries: list = ["bittensor"], limit_number: int = 15) -> list:
        """
        Execute the tweet query process using the specified search queries.

        Args:
            search_queries (list, optional): A list of search terms to be queried. Defaults to ["bittensor"].

        Returns:
            list: A list of tweets.
        """
        raise Exception("This actor does not support general search queries")

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
            'id': item['id'], 
            'url': item['url'], 
            'text': item['text'], 
            'likes': item['likes'],
            'timestamp': str(datetime.fromisoformat(item['timestamp'].replace("Z", "+00:00")))
            } for item in input]
        return filtered_input


if __name__ == '__main__':
    # Initialize the tweet query mechanism
    query = WebHarvesterTwitterScraperQuery()

    # Execute the query for the "bitcoin" search term
    data_set = query.searchByUrl()

    # Output the data
    for item in data_set:
        print(item)
