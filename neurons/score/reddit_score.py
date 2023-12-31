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
import bittensor as bt
from neurons.queries import get_query, QueryType, QueryProvider
import random
from dateutil.parser import parse

reddit_query = get_query(QueryType.REDDIT, QueryProvider.PERCIPIO_REDDIT_LOOKUP)

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
    if len(responses) == 0:
        return []
    
    # Initialize variables
    # Initialize score list. The length of score list is the same as the length of responses.
    score_list = torch.zeros(len(responses))
    # Initialize time difference list. The length of time difference list is the same as the length of responses.
    time_diff_list = torch.zeros(len(responses))

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
    relevant_ratio = torch.zeros(len(responses))

    format_score = torch.zeros(len(responses))
    fake_score = torch.zeros(len(responses))
    
    # Count the number of occurrences of each ID
    id_counts = {}
    for i, response in enumerate(responses):

        if response == None:
            responses[i] = []
            response = []
            format_score[i] = 1
        id_list = []
        for post in response:  
            try:
                # Check that 'text', 'timestamp' and 'dataType' fields exist
                post['text'] and post['timestamp'] and post['dataType']
                if post['id'] in id_list:
                    bt.logging.info(f"Duplicated id found: {post['id']} in response {i}")
                    fake_score[i] = 1
                else:
                    id_list.append(post['id'])

                post_id = post['id']
                id_counts[post_id] = id_counts.get(post_id, 0) + 1
                
            except Exception as e:
                bt.logging.error(f"❌ Error while verifying post: {e}: {post}")
                format_score[i] = 1

    # Choose random responses from each miner to compare, and gather their urls
    spot_check_idx = []
    spot_check_ids = []
    spot_check_posts = []
    for i, response in enumerate(responses):
        if len(response) > 0:
            item_idx = random.randrange(len(response))
            spot_check_idx.append(item_idx)
            spot_check_id = response[item_idx].get('id')
            if spot_check_id is not None:
                spot_check_ids.append(spot_check_id)
        else:
            spot_check_idx.append(None)

    # Fetch spot check urls
    if len(spot_check_ids) > 0:
        try:
            bt.logging.info(f"Validating {len(spot_check_ids)} posts.")
            spot_check_posts = reddit_query.lookup(set(spot_check_ids))
        except Exception as e:
            bt.logging.error(f"❌ Error while verifying post: {e}")

    # Calculate score for each response
    for i, response in enumerate(responses):
        # initialize variables
        similarity_score = 0
        relevant_count = 0
        time_diff_score = 0
        total_length += len(response)

        # update max_length
        max_length = max(len(response), max_length)

        # Do spot check for this miner
        correct_score = 0
        if len(response) > 0:
            sample_item = response[spot_check_idx[i]]
            sample_id = sample_item.get('id', "")
            searched_item = next((post for post in spot_check_posts if post['id'] == sample_id), None)
            if searched_item:
                # Some posts have an empty body, but the apify actor is filling in img/thumbnail in the text
                # Consider that a match
                title_ok = searched_item['dataType'] != "post" or searched_item.get('title') == sample_item.get('title')
                text_ok = len(searched_item['text']) == 0 or searched_item['text'] == sample_item['text']
                if(title_ok and text_ok and searched_item['timestamp'] == sample_item['timestamp']):
                    correct_score = 1
                else:
                    bt.logging.info(f"Tampered post! {sample_item}")
                    bt.logging.info(f"Original post: {searched_item}")
            else: 
                bt.logging.info(f"No result returned for {sample_item}")

        try:
            # calculate scores
            for i_item, item in enumerate(response):
                if tag.lower() in item.get('title', '').lower():
                    relevant_count += 1
                elif tag.lower() in item['text'].lower():
                    relevant_count += 1

                # calculate similarity score
                similarity_score += (id_counts[item['id']] - 1)
                # calculate time difference score
                date_temp = parse(item['timestamp'])
                date_string = date_temp.strftime('%Y-%m-%d %H:%M:%S+00:00')
                date_object = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S+00:00')
                time_diff = datetime.datetime.now() - date_object
                time_diff_score += time_diff.seconds
        except Exception as e:
            bt.logging.info(f"Bad format: {e}")
            format_score[i] = 1

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

        if len(response) > 0:
            relevant_ratio[i] = relevant_count / len(response)
        else:
            relevant_ratio[i] = 0


    similarity_list = (similarity_list + 1) / (max_similar_count + 1)
    time_diff_list = (time_diff_list + 1) / (max_time_diff + 1)
    correct_list = (correct_list + 1) / (max_correct_score + 1)
    length_normalized = (length_list + 1) / (max_length + 1)

    time_diff_contribution = (1 - time_diff_list) * 0.2
    length_contribution = length_normalized * 0.3
    similarity_contribution = (1 - similarity_list) * 0.3
    relevancy_contribution = relevant_ratio * 0.2

    score_list = (similarity_contribution + time_diff_contribution + length_contribution + relevancy_contribution)

    pre_filtered_score = score_list.clone()

    for i, correct_list_item in enumerate(correct_list):
        if correct_list_item < 1:
            score_list[i] = 0
        if format_score[i] == 1:
            score_list[i] = 0
        if fake_score[i] == 1:
            score_list[i] = 0
        if relevant_ratio[i] < 0.5:
            score_list[i] = 0

    for i, response in enumerate(responses):
        if response == [] or response == None:
            score_list[i] = 0

    filtered_scores = score_list.clone()

    # normalize score list

    if torch.sum(score_list) == 0:
        normalized_scores = score_list
    else:
        normalized_scores = score_list / torch.sum(score_list)

    scoring_metrics = {
        "correct": correct_list,
        "similarity": similarity_list,
        "time_diff": time_diff_list,
        "time_contrib": time_diff_contribution,
        "length": length_list,
        "length_contrib": length_contribution,
        "similarity_contrib": similarity_contribution,
        "relevancy_contrib": relevancy_contribution,
        "format": format_score,
        "fake": fake_score,
        "pre_filtered_score": pre_filtered_score,
        "filtered_scores": filtered_scores,
        "normalized_scores": normalized_scores,
    }

    # Convert tensors to arrays
    return {k: [v.item() for v in tensor] for k, tensor in scoring_metrics.items()}
        





    

