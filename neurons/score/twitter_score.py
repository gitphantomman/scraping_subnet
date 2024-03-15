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
from datetime import datetime
import random
import traceback
import bittensor as bt
from urllib.parse import urlparse
import os
import re
import html
from neurons.queries import get_query, QueryType, QueryProvider

twitter_query = get_query(QueryType.TWITTER, QueryProvider.APIDOJO_TWEET_SCRAPER)


def parse_date(dateStr: str):
    return datetime.strptime(dateStr, '%Y-%m-%d %H:%M:%S+00:00')

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
    # Initialize average age list. The length of average age list is the same as the length of responses.
    average_age_list = torch.zeros(len(responses))

    correct_score = 0
    max_correct_score = 0
    max_average_age = 0

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
        for tweet in response:
            try:
                # A single tweet in the response in the far future can usually skip validation, but
                # will effect average age significantly and boost score. A future tweet will invalidate
                # this response.
                date_object = parse_date(tweet['timestamp'])
                age = datetime.utcnow() - date_object
                if age.total_seconds() < 0:
                    bt.logging.warning(f"Faked future tweet: {tweet}")
                    fake_score[i] = 1

                if tweet['id'] in id_list or tweet['id'] not in tweet['url']:
                    fake_score[i] = 1
                else:
                    id_list.append(tweet['id'])
                
                parsed_url = urlparse(tweet['url'])
                # Extract the path from the URL 
                path = parsed_url.path
                # Get the last component of the path
                last_component = os.path.basename(path)
                if last_component != tweet['id']:
                    bt.logging.warning(f"miner {i} id/url mismatch detected: url={tweet['url']}, id={tweet['id']}")
                    fake_score[i] = 1

                tweet_id = tweet['id']
                if tweet_id in id_counts:
                    id_counts[tweet_id] += 1
                else:
                    id_counts[tweet_id] = 1

                if not tweet.get('username'):
                    format_score[i] = 1
                    bt.logging.warning(f"❌ Tweet missing username: {e}, {tweet}")

            except Exception as e:
                bt.logging.warning(f"❌ Bad format for tweet: {e}, {tweet}")
                format_score[i] = 1

    # Choose random responses from each miner to compare, and gather their urls
    spot_check_idx = []
    spot_check_urls = []
    spot_check_tweets = []
    for i, response in enumerate(responses):
        if len(response) > 0:
            item_idx = random.randrange(len(response))
            spot_check_idx.append(item_idx)
            url = response[item_idx].get('url')
            if url and re.search("(twitter.com|x.com)\/\w+\/status\/\d+", url):
                spot_check_urls.append(url)
        else:
            spot_check_idx.append(None)

    # Fetch spot check urls
    if len(spot_check_urls) > 0:
        try:
            spot_check_tweets = []
            found_urls = set()
            tries = 0
            remaining_urls = set(spot_check_urls)
            while tries < 2 and len(remaining_urls) > 0:
                urls = random.sample(sorted(remaining_urls), k=min(20, len(remaining_urls)))
                bt.logging.info(f"Fetching {len(urls)} tweets out of {len(remaining_urls)} remaining to validate.")
                batch_tweets = twitter_query.searchByUrl(urls)
                batch_urls = set([tweet['url'] for tweet in batch_tweets])
                bt.logging.info(f"Fetched {len(batch_urls)}.")
                remaining_urls = remaining_urls - set(batch_urls)
                spot_check_tweets += batch_tweets
                tries += 1
            found_urls = [tweet['url'] for tweet in spot_check_tweets]
            missing_urls = set(spot_check_urls) - set(found_urls)
            bt.logging.info(f"Missing {len(missing_urls)}/{len(spot_check_urls)} tweets.")
        except Exception as e:
            print(traceback.format_exc())
            bt.logging.error(f"❌ Error while verifying tweet: {e}")

    # Calculate score for each response
    for i, response in enumerate(responses):
        # initialize variables
        similarity_score = 0
        relevant_count = 0
        age_sum = 0
        total_length += len(response)
        # calculate max_length
        if len(response) > max_length:
            max_length = len(response)

        # Do spot check for this miner
        correct_score = 0
        if len(response) > 0:
            sample_item = response[spot_check_idx[i]]
            searched_item = next((tweet for tweet in spot_check_tweets if tweet['id'] == sample_item['id']), None)
            if searched_item:
                # Normalize text to account for variations in scraped data.
                miner_text = sample_item['text']
                verify_text = searched_item['text']

                if verify_text != miner_text:
                    bt.logging.info(f"Text does not match! (miner_idx = {i}) {sample_item}")
                    bt.logging.info(f"Original tweet: {searched_item}")
                elif searched_item['timestamp'] != sample_item['timestamp']:
                    bt.logging.info(f"Timestamp does not match! (miner_idx = {i}) {sample_item}")
                    bt.logging.info(f"Original tweet: {searched_item}")
                elif searched_item['username'] != sample_item['username']:
                    bt.logging.info(f"Username does not match! (miner_idx = {i}) {sample_item}")
                    bt.logging.info(f"Original tweet: {searched_item}")
                else:
                    correct_score = 1
            else: 
                bt.logging.info(f"No result returned for {sample_item} (miner_idx={i})")

        # calculate scores
        for item in response:
            if tag.lower() in item['text'].lower() or tag.lower() in item.get('username', '').lower():
                relevant_count += 1
            # calculate similarity score
            similarity_score += (id_counts[item['id']] - 1)
            # calculate time difference score
            try:
                date_object = parse_date(item['timestamp'])
                age = datetime.utcnow() - date_object
                age_sum += age.total_seconds()
            except Exception as e:
                # Mark as fake data if date format incorrect
                fake_score[i] = 1
                bt.logging.info(f"Tweet had bad date format: {e}")

        if max_similar_count < similarity_score:
            max_similar_count = similarity_score
        if max_correct_score < correct_score:
            max_correct_score = correct_score

        similarity_list[i] = similarity_score
        length_list[i] = len(response)
        correct_list[i] = correct_score

        if len(response) > 0:
            relevant_ratio[i] = relevant_count / len(response)
            average_age = age_sum / len(response)
        else:
            relevant_ratio[i] = 0
            average_age = 0 # 0 is the "best" age, but miners with no tweets will still score 0

        if max_average_age < average_age:
            max_average_age = average_age

        average_age_list[i] = average_age


    similarity_list = (similarity_list + 1) / (max_similar_count + 1)
    correct_list = (correct_list + 1) / (max_correct_score + 1)
    length_normalized = (length_list + 1) / (max_length + 1)

    age_contribution = (1 - (average_age_list + 1) / (max_average_age + 1)) * 0.4
    length_contribution = length_normalized * 0.3
    similarity_contribution = (1 - similarity_list) * 0.1
    relevancy_contribution = relevant_ratio * 0.2

    score_list = (similarity_contribution + age_contribution + length_contribution + relevancy_contribution)

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
    # normalize score list
            
    filtered_scores = score_list.clone()

    if torch.sum(score_list) == 0:
        normalized_scores = score_list
    else:
        normalized_scores = score_list / torch.sum(score_list)

    scoring_metrics = {
        "correct": correct_list,
        "similarity": similarity_list,
        "average_age": average_age_list,
        "time_contrib": age_contribution,
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

    return {k: [v.item() for v in tensor] for k, tensor in scoring_metrics.items()}
        


    

