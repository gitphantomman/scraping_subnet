import os
from enum import Enum
from neurons.apify.actors import ActorConfig
from neurons.apify.tweeter.tweet_flush_query import TweetFlushQuery
from neurons.apify.tweeter.tweet_scraper_query import TweetScraperQuery


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
    TWEET_FLUSH = "apify_tweet_flush"


# Mapping between query types and their respective classes
QUERY_MAP = {
    (QueryType.TWITTER, QueryProvider.TWEET_SCRAPER): TweetScraperQuery,
    (QueryType.TWITTER, QueryProvider.TWEET_FLUSH): TweetFlushQuery
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

    # Construct the environment variable key to fetch the actor ID
    actor_id_key = f"{query_provider.value.upper()}_ACTOR_ID"
    actor_id = os.environ.get(actor_id_key)

    if actor_id is None:
        raise Exception(f"Environment variable {actor_id_key} not set")

    # Get the actor configuration
    actor_config = ActorConfig(actor_id)

    # Get the query class from the mapping
    query_class = QUERY_MAP.get((query_type, query_provider))

    if query_class:
        return query_class(actor_config)
    else:
        raise Exception("Invalid query type or query provider")

# Usage example:
# query_instance = get_query(QueryType.TWITTER, QueryProvider.TWEET_SCRAPER)
