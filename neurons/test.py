import boto3
from botocore.client import Config
import csv
import io
from pyathena import connect
import pandas as pd

# Create a session with AWS
session = boto3.Session(
    aws_access_key_id='8FKV07PTHEVL1FNW2C3H',
    aws_secret_access_key='j8zkapwEzabrDM9ghKnXD9znSZV8Ol8HuVvNbbaV',
    region_name='us-central-1'
)

# Create a client with Wasabi endpoint
s3 = session.client(
    's3',
    endpoint_url='https://s3.us-central-1.wasabisys.com',
    config=Config(signature_version='s3v4')
)

# Connect to Athena
conn = connect(aws_access_key_id='8FKV07PTHEVL1FNW2C3H',
               aws_secret_access_key='j8zkapwEzabrDM9ghKnXD9znSZV8Ol8HuVvNbbaV',
               s3_staging_dir='s3://scrapingsubnetbucket/',
               region_name='us-central-1')

# Add a new row to the data
new_row = ['18', 'slkdf', '46', 'sdfsd', '2909']
query = f"INSERT INTO test VALUES {str(tuple(new_row))}"

# Execute the query
pd.read_sql(query, conn)

# Print the new data
print(pd.read_sql('SELECT * FROM test', conn))
