from neurons.apify.apify import ApifyConfig, run_actor

if __name__ == '__main__':
    config = ApifyConfig()
    config.api_key = "apify_api_PWSZ5jVZhtpANm6hPDVTFdPja4Gnqc4kfdd3"

    run_input = {
        "searchQueries": ["career"],
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
        },
    }

    data_set = run_actor("2s3kSMq7tpuC3bI6M", {}, config=config)
    for item in data_set:
        print(item)
