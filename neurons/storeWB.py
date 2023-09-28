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


import wandb
import csv
import pandas as pd

# Function to store all responses from all miners to wandb
def store_reddit(all_data, projectName, run_id):
    """
    This function stores all responses from all miners to wandb.

    Args:
        all_data (list): The list of all data.
        projectName (str): The name of the project.
        run_id (str): The id of the run.
    """

    # Initialize wandb run
    run = wandb.init(project = projectName,  resume="allow",  id = run_id)

    # Collect registered post ids
    historyData= returnRedditdata(project = projectName, id = run_id)
    history_ids = []
    for item in historyData:
        history_ids.append(item['id'])
    
    # Iterate over all data
    for data in all_data:
        # TODO: Add error handling for None data
        if(data is not None):
            for item in data:
                # Check if miner's response already exists in storage
                if item['id'] in history_ids:
                    continue
                # Log the data to wandb
                wandb.log({
                    "id": item['id'],
                    "title": item['title'],
                    "content": item['content'],
                    "url": item['url'],
                    "created_utc": item['created_utc'],
                    "type": item['type']
                })
    # Finish the run
    run.finish()

# Function to store all responses from all miners to wandb for Twitter data
def store_twitter(all_data, projectName, run_id):
    """
    This function stores all responses from all miners to wandb for Twitter data.

    Args:
        all_data (list): The list of all data.
        projectName (str): The name of the project.
        run_id (str): The id of the run.
    """

    # Initialize wandb run
    run = wandb.init(project = projectName, resume="allow", id = run_id)

    # Collect registered post ids
    historyData= returnTwitterData(project = projectName, id = run_id)
    
    history_ids = []
    for index, item in historyData.iterrows():
        history_ids.append(item['id'])

    # Iterate over all data
    for data in all_data:
        # TODO: Add error handling for None data
        if(data is not None):
            for item in data:
                # Check if miner's response already exists in storage
                if item['id'] in history_ids:
                    continue
                # Log the data to wandb
                wandb.log({
                    "id": item['id'],
                    "text": item['text'],
                    "url_hash": item['url_hash'],
                    "url": item['url'],
                    "created_at": item['created_at'],
                    "type": item['type']
                })
    # Finish the run
    run.finish()

# Function to return all data in storage for Reddit data
def returnRedditdata(project = "scraping_subnet-neurons", id = "w8937gls"):
    """
    This function returns all data in storage for Reddit data.

    Args:
        project (str): The name of the project. Defaults to "scraping_subnet-neurons".
        id (str): The id of the run. Defaults to "w8937gls".

    Returns:
        DataFrame: The DataFrame of the history data.
    """
    api = wandb.Api()
    run = api.run(f"aureliojafer/{project}/{id}")
    historyData = run.history()
    return historyData

# Function to output all Reddit data as csv file
def printRedditCSV():
    """
    This function outputs all Reddit data as csv file.

    Returns:
        DataFrame: The DataFrame of the history data.
    """
    api = wandb.Api()
    run = api.run("aureliojafer/scraping_subnet-neurons/w8937gls")
    historyData = run.history()

    # Write the data to a csv file
    with open('outputReddit.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file)
        writer.writeheader()
        writer.writerows(historyData)
    return historyData

# Function to return all data in storage for Twitter data
def returnTwitterData(project = "scraping_subnet-neurons", id = "g1ibv7db"):
    """
    This function returns all data in storage for Twitter data.

    Args:
        project (str): The name of the project. Defaults to "scraping_subnet-neurons".
        id (str): The id of the run. Defaults to "g1ibv7db".

    Returns:
        DataFrame: The DataFrame of the history data.
    """
    api = wandb.Api()
    run = api.run(f"aureliojafer/{project}/{id}")
    historyData = run.history()
    return historyData

# Function to output all Twitter data as csv file
def printTwitterCSV():
    """
    This function outputs all Twitter data as csv file.

    Returns:
        DataFrame: The DataFrame of the history data.
    """
    api = wandb.Api()
    run = api.run("aureliojafer/scraping_subnet-neurons/g1ibv7db")
    historyData = run.history()
    if isinstance(historyData, pd.DataFrame):
        keys = historyData.keys()  # Get column names if historyData is a DataFrame
    else:
        # Handle the case where historyData is not a DataFrame
        keys = historyData.data[0].keys() if hasattr(historyData, 'data') else []
    
    # Write the data to a csv file
    with open('outputTwitter.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        
        if isinstance(historyData, pd.DataFrame):
            # If historyData is a DataFrame, convert it to a list of dictionaries
            writer.writerows(historyData.to_dict(orient='records'))
        else:
            # Handle the case where historyData is not a DataFrame
            writer.writerows(historyData)
    
    return historyData

# Output all Twitter data as csv file.
printTwitterCSV()