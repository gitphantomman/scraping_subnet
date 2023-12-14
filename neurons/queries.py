import os
from enum import Enum
from neurons.apify.actors import ActorConfig
from neurons.apify.tweeter.tweet_flash_query import TweetFlashQuery
from neurons.apify.tweeter.tweet_scraper_query import TweetScraperQuery
from neurons.apify.tweeter.web_harvester_twitter_scraper_query import WebHarvesterTwitterScraperQuery
from neurons.apify.reddit.reddit_scraper_lite import RedditScraperLite
from neurons.apify.reddit.reddit_scraper import RedditScraper
from neurons.apify.reddit.epctex_reddit_scraper import EpctexRedditScraper
from neurons.services.percipio_reddit_lookup import PercipioRedditLookup
from dotenv import load_dotenv

load_dotenv()

class QueryType(Enum):
    """
    Enum representing the different types of queries.
    """
    TWITTER = 1
    REDDIT = 2


class QueryProvider(Enum):
    """
    Enum representing the different providers of queries.
    """
    TWEET_SCRAPER = "apify_tweet_scraper"
    TWEET_FLASH = "apify_tweet_flash"
    WEB_HARVESTER_TWITTER_SCRAPER = "web_harvester_twitter_scraper"
    REDDIT_SCRAPER_LITE = "apify_reddit_scraper_lite"
    REDDIT_SCRAPER = "apify_reddit_scraper"
    EPCTEX_REDDIT_SCRAPER = "epctex_reddit_scraper"
    PERCIPIO_REDDIT_LOOKUP = "percipio_reddit_lookup"


# Mapping between query types and their respective classes
QUERY_MAP = {
    (QueryType.TWITTER, QueryProvider.TWEET_SCRAPER): TweetScraperQuery,
    (QueryType.TWITTER, QueryProvider.TWEET_FLASH): TweetFlashQuery,
    (QueryType.TWITTER, QueryProvider.WEB_HARVESTER_TWITTER_SCRAPER): WebHarvesterTwitterScraperQuery,    
    (QueryType.REDDIT, QueryProvider.REDDIT_SCRAPER_LITE): RedditScraperLite,
    (QueryType.REDDIT, QueryProvider.REDDIT_SCRAPER): RedditScraper,
    (QueryType.REDDIT, QueryProvider.EPCTEX_REDDIT_SCRAPER): EpctexRedditScraper,
    (QueryType.REDDIT, QueryProvider.PERCIPIO_REDDIT_LOOKUP): PercipioRedditLookup
}


def get_query(query_type: QueryType, query_provider: QueryProvider):
    """
    Retrieve an instance of a query based on the given query type and provider.

    Parameters:
    - query_type (QueryType): The type of the query (e.g. TWITTER).
    - query_provider (QueryProvider): The provider of the query (e.g. TWEET_SCRAPER).

    Returns:
    An instance of the specified query.

    Raises:
    Exception: If the required environment variable for the actor ID is not set.
    Exception: If an invalid query type or provider is given.
    """

    # Get the query class from the mapping
    query_class = QUERY_MAP.get((query_type, query_provider))

    if query_class:
        return query_class()
    else:
        raise Exception("Invalid query type or query provider")

