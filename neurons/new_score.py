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

# importing necessary libraries and modules

import torch
import datetime

def calculateScore(responses = [], tag = 'tao'):
    """
    This function calculates the score of responses.
    The score is calculated by the degree of similarity between responses, accuracy and time difference.
    Args:
        responses (list): The list of responses.
        tag (str): The tag of responses.
    Returns:
        list: The list of scores for each response.
    """
    
    # Check if responses is empty
    if len(responses) == 0:
        return []
    
    # Initialize variables
    # Initialize score list. The length of score list is the same as the length of responses.
    score_list = torch.zeros(len(responses))
    # Initialize time difference list. The length of time difference list is the same as the length of responses.
    time_diff_list = torch.zeros(len(responses))
    total_time_diff = 0
    max_time_diff = 0
    # Initialize accuracy list. The length of accuracy list is the same as the length of responses.
    accuracy_list = torch.zeros(len(responses))
    # Initialize similarity list. The length of similarity list is the same as the length of responses.
    similarity_list = torch.zeros(len(responses))
    max_similar_count = 0
    # Initialize length list. The length score list is the same as the length of responses.
    length_list = torch.zeros(len(responses))
    total_length = 0
    max_length = 0

    total_similarity_score = 0
    # Count the number of occurrences of each ID
    id_counts = {}
    for response in responses:
        for tweet in response:
            tweet_id = tweet['id']
            if tweet_id in id_counts:
                id_counts[tweet_id] += 1
            else:
                id_counts[tweet_id] = 1


    # Calculate score for each response
    for i, response in enumerate(responses):
        # initialize variables
        similarity_score = 0
        time_diff_score = 0
        total_length += len(response)

        # calculate max_length
        if len(response) > max_length:
            max_length = len(response)
        # calculate scores
        for i_item, item in enumerate(response):
            # caluclate similarity score
            similarity_score += (id_counts[item['id']] - 1)
            # calculate time difference score
            date_object = datetime.datetime.strptime(item['timestamp'], '%Y-%m-%d %H:%M:%S+00:00')
            time_diff = datetime.datetime.now() - date_object
            time_diff_score += time_diff.seconds
            
        total_similarity_score += similarity_score
        total_time_diff += time_diff_score

        if max_similar_count < similarity_score:
            max_similar_count = similarity_score
        if max_time_diff < time_diff_score:
            max_time_diff = time_diff_score

        similarity_list[i] = similarity_score
        time_diff_list[i] = time_diff_score
        length_list[i] = len(response)

    similarity_list = (similarity_list + 1) / (max_similar_count + 1)
    time_diff_list = (time_diff_list + 1) / (max_time_diff + 1)
    length_list = length_list / max_length

    print(f"similarity_list: {similarity_list}")
    print(f"time_diff_list: {time_diff_list}")
    print(f"length_list: {length_list}")
        
    score_list = (similarity_list * 0.3  + time_diff_list * 0.2 + length_list * 0.5)
    return score_list
        


    

