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
from neurons.apify.queries import get_query, QueryType, QueryProvider
import random

twitter_query = get_query(QueryType.TWITTER, QueryProvider.TWEET_FLUSH)

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
    # :TODO Tao based score calculation
    # :TODO make variables for setting query type and provider
    # Check if responses is empty
    if len(responses) == 0:
        return []
    
    # Initialize variables
    # Initialize score list. The length of score list is the same as the length of responses.
    score_list = torch.zeros(len(responses))
    # Initialize time difference list. The length of time difference list is the same as the length of responses.
    time_diff_list = torch.zeros(len(responses))
    total_time_diff = 0
    correct_score = 0
    max_correct_score = 0
    max_time_diff = 0
    # Initialize accuracy list. The length of accuracy list is the same as the length of responses.
    accuracy_list = torch.zeros(len(responses))
    # Initialize similarity list. The length of similarity list is the same as the length of responses.
    similarity_list = torch.zeros(len(responses))
    max_similar_count = 0
    # Initialize length list. The length score list is the same as the length of responses.
    length_list = torch.zeros(len(responses))
    correct_list = torch.ones(len(responses))
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

    samples_for_compare = []
    
    if (len(responses) > 3):
        # * Choose 3 random responses to compare and return their index. You can change the number of samples by changing k
        compare_list = random.sample(list(range(len(responses))), k=3)
    else:
        compare_list = list(range(len(responses)))
    # Calculate score for each response
    for i, response in enumerate(responses):
        # initialize variables
        similarity_score = 0
        time_diff_score = 0
        total_length += len(response)
        correct_score = 1
        # calculate max_length
        if len(response) > max_length:
            max_length = len(response)

        # choose two itmems to compare
        if (i in compare_list):
            correct_score = 0
            sample_indices = random.sample(list(range(len(response))), k=1) # * Create a list of index numbers. You can conrtol k to change the number of samples
            sample_items = [response[j] for j in sample_indices] # Get the corresponding items from the response list
            for sample_item in sample_items:
                searched_item = twitter_query.searchByUrl([sample_item['url']])
                if searched_item:
                    if(searched_item[0]['text'] == sample_item['text'] and searched_item[0]['timestamp'] == sample_item['timestamp']):
                        correct_score += 1
                else: 
                    correct_score += 0
            correct_score /= len(sample_items)
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
        if max_correct_score < correct_score:
            max_correct_score = correct_score

        similarity_list[i] = similarity_score
        time_diff_list[i] = time_diff_score
        length_list[i] = len(response)
        correct_list[i] = correct_score


    

    similarity_list = (similarity_list + 1) / (max_similar_count + 1)
    time_diff_list = (time_diff_list + 1) / (max_time_diff + 1)
    correct_list = (correct_list + 1) / (max_correct_score + 1)
    length_list = (length_list + 1) / (max_length + 1)

        
    score_list = ((1 - similarity_list) * 0.15 + correct_score * 0.3  + (1 - time_diff_list) * 0.15 + length_list * 0.4)
    # normalize score list
    score_list = score_list / torch.sum(score_list)
    return score_list
        


    

