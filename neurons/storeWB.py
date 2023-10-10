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
def store_reddit(all_data, username, projectName, run_id):
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
    historyData= returnData(username = username, project = projectName, id = run_id)
    
   
    
    # Iterate over all data
    for data in all_data:
        # TODO: Add error handling for None data
        if(data is not None):
            for item in data:
                # Check if miner's response already exists in storage
                # Check if history is empty
                if historyData.empty or historyData is None:
                    wandb.log({
                        "id": item['id'],
                        "title": item['title'],
                        "text": item['text'],
                        "url": item['url'],
                        "created_at": item['created_at'],
                        "type": item['type']
                    })
                else:
                    filtered_data = historyData[historyData['id'] == item['id']]
                    # Log the data to wandb
                    if filtered_data.empty or filtered_data is None:
                        wandb.log({
                            "id": item['id'],
                            "title": item['title'],
                            "text": item['text'],
                            "url": item['url'],
                            "created_at": item['created_at'],
                            "type": item['type']
                        })
    # Finish the run
    run.finish()

# Function to store all responses from all miners to wandb for Twitter data
def store_twitter(all_data,username, projectName, run_id):
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
    historyData= returnData(username = username, project = projectName, id = run_id)
    
    # history_ids = []
    # for index, item in historyData.iterrows():
    #     history_ids.append(item['id'])

    # Iterate over all data
    for data in all_data:
        if data is not None:
            for item in data:
                # Check if miner's response already exists in storage
                # Check if post already exists in history
                if historyData.empty or historyData is None:
                    # Log the data to wandb
                    wandb.log({
                        "id": item['id'],
                        "text": item['text'],
                        "url": item['url'],
                        "created_at": item['created_at'],
                        "type": item['type']
                    })
                else: 
                    filtered_data = historyData[historyData['id'] == item['id']]
                    if filtered_data.empty or filtered_data is None:
                        # Log the data to wandb
                        wandb.log({
                            "id": item['id'],
                            "text": item['text'],
                            "url": item['url'],
                            "created_at": item['created_at'],
                            "type": item['type']
                        })
        else:
            print("No data found")
    # Finish the run
    run.finish()




# Function to return all data in storage for Twitter data
def returnData(username, project, id):
    """
    This function returns all data in storage for Twitter data.

    Args:
        project (str): The name of the project. Defaults to "scraping_subnet-neurons".
        id (str): The id of the run. Defaults to "g1ibv7db".

    Returns:
        DataFrame: The DataFrame of the history data.
    """
    api = wandb.Api()
    run = api.run(f"{username}/{project}/{id}")
    historyData = run.history()
    return historyData

