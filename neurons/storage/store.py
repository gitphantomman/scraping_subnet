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



def twitter_store(data = [], search_keys = []):
    id_list = []
    filename = 'twitter_' + generate_random_string() + '.csv'

    csv_buffer = StringIO()
    fieldnames = ['id', 'url', 'text', 'likes', 'images', 'timestamp']

    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)

    writer.writeheader()
    total_count = 0
    for response in data:
        if response != [] and response != None:
            for item in response:
                if item['id'] in id_list or item['id'] == None:
                    continue
                else:
                    id_list.append(item['id'])
                    if item['id'] != None and item['url'] != None and item['text'] != None and item['likes'] != None and item['images'] != None and item['timestamp'] != None:
                        writer.writerow(item)
                        total_count += 1
    if total_count > 0:
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
    fieldnames = ['id', 'url', 'text', 'likes', 'dataType', 'timestamp']

    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
    total_count = 0
    writer.writeheader()
    for response in data:
        if response != [] and response != None:
            for item in response:
                print(item)
                if item['id'] in id_list or item['id'] == None:
                    continue
                else:
                    id_list.append(item['id'])
                    if item['id'] != None and item['url'] != None and item['text'] != None and item['likes'] != None and item['dataType'] != None and item['timestamp'] != None:
                        writer.writerow(item)
                        total_count += 1
    print(total_count)      
    if total_count > 0:
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



