import logging
from neurons.apify.actors import run_actor, ActorConfig


class TweetScraperQuery:

    def __init__(self, actor_config):
        self.actor_config = actor_config

    def execute(self, search_queries=["bittensor"]):
        run_input = {
            "searchQueries": search_queries,
            "tweetsDesired": 10,
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

    def map(self, input):
        return input


if __name__ == '__main__':
    _config = ActorConfig()
    _config.api_key = "apify_api_PWSZ5jVZhtpANm6hPDVTFdPja4Gnqc4kfdd3"
    _config.actor_id = "2s3kSMq7tpuC3bI6M"

    query = TweetScraperQuery(actor_config=_config)
    data_set = query.execute(search_queries=["bitcoin"])

    for item in data_set:
        print(item)
