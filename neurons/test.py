import boto3
import csv
import random
import string
import time
from io import StringIO

s3 = boto3.resource('s3',
    endpoint_url='https://s3.us-central-1.wasabisys.com',
    aws_access_key_id='O98TI85AO7U2MLKKT1TT',
    aws_secret_access_key='hNHIzr1NedzgfP8GiIHrHsaG779vg6pYvDZq1BcR')

def generate_random_string(length=10):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

def generate_mock_data():
    return {
        'id': generate_random_string(),
        'text': generate_random_string(),
        'timestamp': time.time()
    }

filename = generate_random_string() + '.csv'

csv_buffer = StringIO()
fieldnames = ['id', 'text', 'timestamp']
writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)

writer.writeheader()
for _ in range(10):
    data = generate_mock_data()
    writer.writerow(data)

s3.Bucket('scrapingsubnetbucket').put_object(Key=filename, Body=csv_buffer.getvalue())

csv_buffer.close()
