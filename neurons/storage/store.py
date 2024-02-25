import boto3
import csv
import random
import string
import time
from io import StringIO
from dotenv import load_dotenv
import os
import requests
import json
import bittensor as bt

load_dotenv()
wasabi_endpoint_url = os.getenv("WASABI_ENDPOINT_URL")
access_key_id = os.getenv("WASABI_ACCESS_KEY_ID")
secret_access_key = os.getenv("WASABI_ACCESS_KEY")
indexing_api_key = os.getenv("INDEXING_API_KEY")
s3 = boto3.resource('s3',
    endpoint_url=wasabi_endpoint_url,
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key)

def generate_random_string(length=10):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

def scoring_bucket():
    return s3.Bucket('scoring')

def store_scoring_metrics(metrics: dict, type: str):
    block = metrics['block']
    filename = f"{block:09}_{generate_random_string()}.json"
    data = json.dumps(metrics)
    key = f"{type}/{filename}"
    s3.Bucket('scoring').put_object(Key=key, Body=data)
    bt.logging.info(f"Stored scoring metrics to {key}")

def twitter_store(data = [], search_keys = []):
    id_list = []
    filename = 'twitter_' + generate_random_string() + '.csv'

    csv_buffer = StringIO()
    required_fields = ['id', 'url', 'text', 'likes', 'images', 'timestamp']
    fieldnames = ['id', 'url', 'text', 'likes', 'images', 'timestamp', 'username', 'hashtags']

    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)

    writer.writeheader()
    total_count = 0
    for response in data:
        if response != [] and response != None:
            for item in response:

                # Check if all required keys are present in the dictionary
                if not all(key in item and item[key] is not None for key in required_fields):
                    continue

                if item['id'] in id_list or item['id'] == None:
                    continue
                else:
                    id_list.append(item['id'])
                    # Remove any non-standard keys
                    item = {key: value for key, value in item.items() if key in fieldnames}
                    writer.writerow(item)
                    total_count += 1

    if total_count > 0:
        bt.logging.info(f"Storing {total_count} results as twitterscrapingbucket/twitter/{filename}")
        s3.Bucket('twitterscrapingbucket').put_object(Key='twitter/' + filename, Body=csv_buffer.getvalue())

        csv_buffer.close()
        indexing_result = save_indexing_row(file_name=filename, source_type="twitter", row_count=total_count, search_keys=search_keys)
        return indexing_result
    else:
        return {"msg": "data length is 0"}

def reddit_store(data = [], search_keys = []):
    id_list = []
    filename = 'reddit_' + generate_random_string() + '.csv'

    csv_buffer = StringIO()
    required_fields = ['id', 'url', 'text', 'likes', 'dataType', 'timestamp']
    fieldnames = ['id', 'url', 'text', 'likes', 'dataType', 'timestamp', 'username', 'parent', 'community', 'title', 'num_comments', 'user_id']

    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
    total_count = 0
    writer.writeheader()
    for response in data:
        if response != [] and response != None:
            for item in response:

                # Check if all required keys are present in the dictionary
                if not all(key in item and item[key] is not None for key in required_fields):
                    continue
 
                # Avoid duplicates
                if item['id'] in id_list or item['id'] == None:
                    continue
                else:
                    id_list.append(item['id'])
                    # Remove any non-standard keys
                    item = {key: value for key, value in item.items() if key in fieldnames}
                    writer.writerow(item)
                    total_count += 1
  
    if total_count > 0:
        bt.logging.info(f"Storing {total_count} results as redditscrapingbucket/reddit/{filename}")
        s3.Bucket('redditscrapingbucket').put_object(Key='reddit/' + filename, Body=csv_buffer.getvalue())

        csv_buffer.close()
        indexing_result = save_indexing_row(file_name=filename, source_type="reddit", row_count=total_count, search_keys=search_keys)
        return indexing_result
    else:
        return {"msg": "data length is 0"}

def save_indexing_row(file_name, source_type, row_count, search_keys = []):


    url = "http://45.77.168.167:8000/addRow"
    
    payload = json.dumps({
    "file_name": file_name,
    "source_type": source_type,
    "row_count": row_count,
    "search_keys": search_keys,
    "api_key": indexing_api_key
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.text



