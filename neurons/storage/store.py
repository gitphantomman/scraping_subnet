import boto3
import csv
import random
import string
import time
from io import StringIO
from dotenv import load_dotenv
import os
load_dotenv()
wasabi_endpoint_url = os.getenv("WASABI_ENDPOINT_URL")
access_key_id = os.getenv("WASABI_ACCESS_KEY_ID")
secret_access_key = os.getenv("WASABI_ACCESS_KEY")
s3 = boto3.resource('s3',
    endpoint_url=wasabi_endpoint_url,
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key)

def generate_random_string(length=10):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))



def twitter_store(data = []):
    filename = 'twitter_' + generate_random_string() + '.csv'

    csv_buffer = StringIO()
    fieldnames = ['id', 'url', 'text', 'likes', 'images', 'timestamp']

    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)

    writer.writeheader()
    for response in data:
        if response != [] and response != None:
            writer.writerows(response)

    s3.Bucket('twitterscrapingbucket').put_object(Key='twitter/' + filename, Body=csv_buffer.getvalue())

    csv_buffer.close()

def reddit_store(data = []):
    filename = 'reddit_' + generate_random_string() + '.csv'

    csv_buffer = StringIO()
    fieldnames = ['id', 'url', 'text', 'likes', 'dataType', 'timestamp']

    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)

    writer.writeheader()
    for response in data:
        if response != [] and response != None:
            writer.writerows(response)

    s3.Bucket('redditscrapingbucket').put_object(Key='reddit/' + filename, Body=csv_buffer.getvalue())

    csv_buffer.close()


