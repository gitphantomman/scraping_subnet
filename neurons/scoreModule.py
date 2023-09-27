from datetime import datetime
import storeWB


# calculate score about miner's respopse
def redditScore( response ):
    timeScore = 1
    total_time_diff = 0
    unique_score = 1
    exist_count = 0
    history = storeWB.returnRedditdata()
    history_ids = []
    # check if the scraped data already exists in storage
    for item in history:
        history_ids.append(item['id'])
    if(response is not None):
        # caluclate average time difference from current time
        for post in response:
            given_time = datetime.fromisoformat(post['created_utc'])
            current_time = datetime.now()
            time_diff = (current_time - given_time).total_seconds()
            total_time_diff += time_diff
            if post['id'] in history_ids:
                exist_count += 1
        unique_score = exist_count / len(response)
        avg_time_diff = total_time_diff / len(response)
        if avg_time_diff < 864000 :
            timeScore = avg_time_diff / 864000
        else:
            timeScore = 1.0
        # return score calculated by time score and unique score
        return 1 - 0.15 * timeScore - 0.5 * unique_score
    else:
        return 0
    

# calculate score about miner's respopse
def twitterScore( response ):
    timeScore = 1
    total_time_diff = 0
    unique_score = 1
    exist_count = 0
    history = storeWB.returnTwitterData()
    history_ids = []
    # check if the scraped data already exists in storage
    for index, item in history.iterrows():
        history_ids.append(item['id'])
    if(response is not None):
        # caluclate average time difference from current time
        for post in response:
            given_time = datetime.fromisoformat(post['created_at'])
            current_time = datetime.now()
            time_diff = (current_time - given_time).total_seconds()
            total_time_diff += time_diff
            if post['id'] in history_ids:
                exist_count += 1
        unique_score = exist_count / len(response)
        avg_time_diff = total_time_diff / len(response)
        if avg_time_diff < 864000 :
            timeScore = avg_time_diff / 864000
        else:
            timeScore = 1.0
        # return score calculated by time score and unique score
        return 1 - 0.15 * timeScore - 0.5 * unique_score
    else:
        return 0
    
def checkScore(responses = ['apple', 'beer', 'apple', 'beer', 'apple', 'heart', 'apple']):
    result = {}
    score = {}
    total_count = len(responses)
    for idx, response in enumerate(responses):
        if response in result:
            result[response].append(idx)
        else:
            result[response] = [idx]
    for key, value in result.items():
        if(key == "NONE"):
            concensus = 0
        concensus = len(value) / total_count
        if concensus >= 0.5:
            for id in value:
                score[f'{id}'] = 1
        else:
            for id in value:
                score[f'{id}'] = concensus
    scoreArray = []
    for i in range(0, len(responses)):
        scoreArray.append(score[f'{i}'])
    # print(scoreArray)
    return scoreArray
checkScore()