from datetime import datetime
import storeWB


# Function to calculate score based on miner's response from Reddit
def redditScore( response ):
    """
    This function calculates a score based on the response from Reddit.
    The score is calculated based on the time difference from the current time and the uniqueness of the response.

    Args:
        response (list): The response from Reddit.

    Returns:
        float: The calculated score.
    """
    # Initialize variables
    timeScore = 1
    total_time_diff = 0
    unique_score = 1
    exist_count = 0

    # Fetch historical data
    history = storeWB.returnRedditdata()
    history_ids = [item['id'] for item in history]

    # TODO: Add error handling for empty response
    if(response is not None):
        # Calculate average time difference from current time
        for post in response:
            given_time = datetime.fromisoformat(post['created_utc'])
            current_time = datetime.now()
            time_diff = (current_time - given_time).total_seconds()
            total_time_diff += time_diff

            # Check if post already exists in history
            if post['id'] in history_ids:
                exist_count += 1

        # Calculate unique score and average time difference
        unique_score = exist_count / len(response)
        avg_time_diff = total_time_diff / len(response)

        # Calculate time score
        if avg_time_diff < 864000 :
            timeScore = avg_time_diff / 864000
        else:
            timeScore = 1.0

        # Return score calculated by time score and unique score
        return 1 - 0.15 * timeScore - 0.5 * unique_score
    else:
        return 0
    

# Function to calculate score based on miner's response from Twitter
def twitterScore( response ):
    """
    This function calculates a score based on the response from Twitter.
    The score is calculated based on the time difference from the current time and the uniqueness of the response.

    Args:
        response (list): The response from Twitter.

    Returns:
        float: The calculated score.
    """
    # Initialize variables
    timeScore = 1
    total_time_diff = 0
    unique_score = 1
    exist_count = 0

    # Fetch historical data
    history = storeWB.returnTwitterData()
    history_ids = [item['id'] for index, item in history.iterrows()]

    # TODO: Add error handling for empty response
    if(response is not None):
        # Calculate average time difference from current time
        for post in response:
            given_time = datetime.fromisoformat(post['created_at'])
            current_time = datetime.now()
            time_diff = (current_time - given_time).total_seconds()
            total_time_diff += time_diff

            # Check if post already exists in history
            if post['id'] in history_ids:
                exist_count += 1

        # Calculate unique score and average time difference
        unique_score = exist_count / len(response)
        avg_time_diff = total_time_diff / len(response)

        # Calculate time score
        if avg_time_diff < 864000 :
            timeScore = avg_time_diff / 864000
        else:
            timeScore = 1.0

        # Return score calculated by time score and unique score
        return 1 - 0.15 * timeScore - 0.5 * unique_score
    else:
        return 0
    

# Function to check the score of responses
def checkScore(responses):
    """
    This function checks the score of responses.

    Args:
        responses (list): The list of responses.

    Returns:
        list: The list of scores for each response.
    """
    result = {}
    score = {}
    total_count = len(responses)

    # TODO: Add error handling for empty responses
    for idx, response in enumerate(responses):
        if response in result:
            result[response].append(idx)
        else:
            result[response] = [idx]

    for key, value in result.items():
        if(key == "NONE"):
            concensus = 0
        concensus = len(value) / total_count

        # Calculate score based on consensus
        if concensus >= 0.5:
            for id in value:
                score[f'{id}'] = 1
        else:
            for id in value:
                score[f'{id}'] = concensus

    # Create score array
    scoreArray = [score[f'{i}'] for i in range(0, len(responses))]

    return scoreArray

checkScore()