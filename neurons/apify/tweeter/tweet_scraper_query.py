from neurons.apify.apify import ApifyConfig, run_actor


class TweetScraperQuery:

    def __init__(self, search_queries=["bittensor"]):
        self.run_input = {
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

    def execute(self, config=None):
        if config is None:
            config = ApifyConfig()
        return self.map(run_actor(config, self.run_input))

    def map(self, input):
        return input


if __name__ == '__main__':
    _config = ApifyConfig()
    _config.api_key = "apify_api_PWSZ5jVZhtpANm6hPDVTFdPja4Gnqc4kfdd3"
    _config.actor_id = "2s3kSMq7tpuC3bI6M"

    query = TweetScraperQuery(search_queries=["bitcoin"])
    data_set = query.execute(config=_config)

    for item in data_set:
        print(item)
