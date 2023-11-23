import logging
from neurons.apify.actors import run_actor, ActorConfig
from datetime import datetime

# Setting up logger for debugging and information purposes
logger = logging.getLogger(__name__)

class EpctexRedditScraper:
    """
    A class designed to scrap reddit posts based on specific search queries using the Apify platform.

    Attributes:
        actor_config (ActorConfig): Configuration settings specific to the Apify actor.
    """

    def __init__(self):
        """
        Initialize the EpctexRedditScraper.
        """
        self.actor_config = ActorConfig("jwR5FKaWaGSmkeq2b")

    def searchByUrl(self, urls: list = ["https://twitter.com/elonmusk/status/1384874438472844800"]):
        run_input = {
            "customMapFunction": "(object) => { return {...object} }",
            "endPage": 1,
            "extendOutputFunction": "($) => { return {} }",
            "includeComments": True,
            "proxy": {
                "useApifyProxy": True
            },
            "startUrls": urls,
            "sort": "relevance",
            "time": "all"
        }

        posts = run_actor(self.actor_config, run_input)

        # Flatten list, un-nesting comments
        def flatten_comments(comments, flat_list):
            for comment in comments:
                flat_list.append({
                    'id': comment['id'],
                    'url': comment['url'],
                    'text': comment['body'],
                    'score': comment['score'],
                    'type': 'comment',
                    'createdAt': comment['createdAt'],
                })
                if comment.get('replies') != None:
                    flatten_comments(comment['replies'], flat_list)

        all_items = []

        for post in posts:
            flatten_comments(post['comments'], all_items)
            all_items.append({                    
                    'id': post['id'],
                    'url': post['url'],
                    'text': post['text'],
                    'score': post['score'],
                    'type': post['type'],
                    'createdAt': post['createdAt'],
            })

        return self.map(all_items)

    def execute(self, search_queries: list = ["bittensor"], limit_number: int = 15) -> list:
        """
        Execute the tweet flushing process using the specified search queries.

        Args:
            search_queries (list, optional): A list of search terms to be queried. Defaults to ["bittensor"].

        Returns:
            list: A list of flushed tweet data.
        """
        run_input = {
            "customMapFunction": "(object) => { return {...object} }",
            "endPage": 1,
            "extendOutputFunction": "($) => { return {} }",
            "includeComments": True,
            "maxItems": limit_number,
            "proxy": {
                "useApifyProxy": True
            },
            "search": search_queries[0],
            "searchMode": "link",
            "sort": "relevance",
            "time": "all"
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
        filtered_input = [
            {'id': item['id'], 
             'url': item['url'],
             'title': item.get('title'),
             'text': item['text'], 
             'likes': item['score'], 
             'dataType': item['type'], 
             'timestamp': datetime.utcfromtimestamp(item['createdAt']).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
             } for item in input]
        return filtered_input


if __name__ == '__main__':
    # Initialize the EpctexRedditScraper query mechanism
    query = EpctexRedditScraper()

    # Execute the flush for the "bitcoin" search term
    #data_set = query.execute(search_queries=["bitcoin"])
    data_set = query.searchByUrl(urls=["https://www.reddit.com/r/Arbitrum/comments/180jrqm/top_3_dapps/ka6t2dv/"])

    # Output the flushed data
    for item in data_set:
        print(item)
