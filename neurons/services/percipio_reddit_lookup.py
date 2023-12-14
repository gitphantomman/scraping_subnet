
import requests

class PercipioRedditLookup:
    """
    A class for verifing reddit ids from the percip.io service
    """

    def __init__(self):
        pass

    def lookup(self, ids: [int] = ["bittensor"]) -> list:
        """
        Find reddit posts/comments by id. Id should be full name form, with prefix, for example: t3_17mhoqv

        Args:
            ids (list, required): A list of reddit ids.

        Returns:
            list: A list of reddit posts/comments/etc.
        """

        ids_str = ','.join(ids)
        url = 'https://api.percip.io/reddit_ids/' + ids_str
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse JSON data
            return response.json()
        else:
            print('Failed to retrieve data')
            return []

if __name__ == '__main__':
    # Initialize the tweet scraper query mechanism with the actor configuration
    query = PercipioRedditLookup()

    # Execute the scraper for the "bitcoin" search term
    data_set = query.lookup(ids=['t3_17mhoqv', 't3_14nbyy2', 't3_15ikdeu'])

    # Output the scraped data
    for item in data_set:
        print(item)
