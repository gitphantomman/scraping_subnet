import os
from enum import Enum
from neurons.apify.actors import ActorConfig
from neurons.apify.tweeter.tweet_flush_query import TweetFlushQuery
from neurons.apify.tweeter.tweet_scraper_query import TweetScraperQuery


class QueryType(Enum):
    TWITTER = 1
    REDDIT = 2


class QueryProvider(Enum):
    TWEET_SCRAPER = "tweet_scraper"
    TWEET_FLUSH = "tweet_flush"


QUERY_MAP = {
    (QueryType.TWITTER, QueryProvider.TWEET_SCRAPER): TweetScraperQuery,
    (QueryType.TWITTER, QueryProvider.TWEET_FLUSH): TweetFlushQuery
}


def get_query(query_type: QueryType, query_provider: QueryProvider):
    actor_id_key = f"{query_provider.value.upper()}_ACTOR_ID"
    actor_id = os.environ.get(actor_id_key)
    if actor_id is None:
        raise Exception(f"Environment variable {actor_id_key} not set")

    actor_config = ActorConfig(actor_id)
    query_class = QUERY_MAP.get((query_type, query_provider))
    if query_class:
        return query_class(actor_config)
    else:
        raise Exception("Invalid query type or query provider")


# Usage example:
# query_instance = get_query(QueryType.TWITTER, QueryProvider.TWEET_SCRAPER)
