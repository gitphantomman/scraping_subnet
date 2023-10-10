"""
The MIT License (MIT)
Copyright © 2023 Chris Wilson

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the “Software”), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of
the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from datetime import datetime
import storeWB



# Function to calculate score based on miner's response from Reddit
def redditScore( response, project = 'scraping_subnet-neurons', run_id = 'w8937gls' ):
    """
    This function calculates a score based on the response from Miner.
    The score is calculated based on the time difference from the current time and the uniqueness of the response.

    Args:
        response (list): The response from Miner.

    Returns:
        float: The calculated score.
    """
    # Initialize all variables
    timeScore = 1
    unique_score = 1

    total_time_diff = 0
    exist_count = 0

    total_length = 0
    wrong_count = 0
    # Fetch historical data
    history = storeWB.returnData(project=project, id=run_id)

    if response is not None and response != []:
        total_length = len(response)
        # Choose 50 random posts from the response
        if len(response) > 50:
            response = random.sample(response, 50)
        
        # Calculate total time difference from current time and count of existing posts
        for post in response:
            # Calculate total time difference from current time
            given_time = datetime.fromisoformat(post['created_at'])
            current_time = datetime.now()
            total_time_diff += (current_time - given_time).total_seconds()
            
            # Check if post already exists in history
            # Check if history is empty
            if history.empty or history is None:
                break
            else:
                filtered_data = history[history['id'] == post['id']]
                print("filterd_data", filtered_data)
                if filtered_data.empty or filtered_data is None:
                    # TODO: check url_hash is correct
                    # TODO: validator scrap that post with url and compare created_at
                    break
                else:
                    exist_count += 1
                    filtered_data = filtered_data.iloc[0]
                    if filtered_data['created_at'] != post['created_at']:
                        wrong_count += 1
        print(exist_count, wrong_count)
        # Calculate unique score and average time difference
        unique_score = (exist_count + 1) / min((len(response) + 1), 50)
        avg_time_diff = total_time_diff / min((len(response) + 1), 50)
        wrong_score = wrong_count / min((len(response) + 1), 50)
        # Calculate time score
        if avg_time_diff < 864000 :
            timeScore = avg_time_diff / 864000
        else:
            timeScore = 1.0

        # Return score calculated by time score and unique score
        return max(1 - 0.1 * timeScore - 0.3 * unique_score - 0.2 * wrong_score - min(0.2, 20 / total_length), 0)
    else:
        return 0
    
import random
# Function to calculate score based on miner's response from Twitter
def twitterScore( response , project = 'scraping_subnet-neurons', run_id = 'g1ibv7db'):
    """
    This function calculates a score based on the response from Miner.
    The score is calculated based on the time difference from the current time and the uniqueness of the response.

    Args:
        response (list): The response from Miner.

    Returns:
        float: The calculated score.
    """
    # Initialize all variables
    timeScore = 1
    unique_score = 1

    total_time_diff = 0
    exist_count = 0
    total_length = 0
    wrong_count = 0
    # Fetch historical data
    history = storeWB.returnData(project=project, id=run_id)

    if response is not None and response != []:
        # Choose 50 random posts from the response
        total_length = len(response)
        if len(response) > 50:
            response = random.sample(response, 50)
        
        # Calculate total time difference from current time and count of existing posts
        for post in response:
            # Calculate total time difference from current time
            given_time = datetime.fromisoformat(post['created_at'])
            current_time = datetime.now()
            total_time_diff += (current_time - given_time).total_seconds()
            
            # Check if post already exists in history
            # Check if history is empty
            if history.empty or history is None:
                break
            else: 
                filtered_data = history[history['id'] == post['id']]
                print("filterd_data", filtered_data)
                if filtered_data.empty or filtered_data is None:
                    # TODO: check url_hash is correct
                    # TODO: validator scrap that post with url and compare created_at
                    break
                else:
                    exist_count += 1
                    filtered_data = filtered_data.iloc[0]
                    if filtered_data['created_at'] != post['created_at']:
                        wrong_count += 1
        print(exist_count, wrong_count)
        # Calculate unique score and average time difference
        unique_score = (exist_count + 1) / min((len(response) + 1), 50)
        avg_time_diff = total_time_diff / min((len(response) + 1), 50)
        wrong_score = wrong_count / min((len(response) + 1), 50)
        # Calculate time score
        if avg_time_diff < 864000 :
            timeScore = avg_time_diff / 864000
        else:
            timeScore = 1.0

        # Return score calculated by time score and unique score
        return max(1 - 0.1 * timeScore - 0.3 * unique_score - 0.2 * wrong_score - min(0.2, 20 / total_length), 0)
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
