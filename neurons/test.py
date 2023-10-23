from neurons.apify.queries import get_query, QueryType, QueryProvider

query = get_query(QueryType.TWITTER, QueryProvider.TWEET_FLUSH)

# Execute the query
tweets = query.execute(["bittensor"])
print(f"number of tweets:{len(tweets)}")
print("---------------------")
print(tweets)

