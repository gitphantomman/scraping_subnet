import wandb
import csv
import pandas as pd
# * Store all responses from all miners to wandb
def store(all_data, projectName, run_id):

    run = wandb.init(project = projectName,  resume="allow",  id = run_id)

    # * collect registered post ids
    historyData= returnRedditdata(project = projectName, id = run_id)
    history_ids = []
    for item in historyData:
        history_ids.append(item['id'])
    
    for data in all_data:
        if(data is not None):
            for item in data:
                # check if miner's response already exists in storage
                if item['id'] in history_ids:
                    continue
                wandb.log({
                    "id": item['id'],
                    "title": item['title'],
                    "content": item['content'],
                    "url": item['url'],
                    "created_utc": item['created_utc'],
                    "type": item['type']
                })
    run.finish()

def store_twitter(all_data, projectName, run_id):

    run = wandb.init(project = projectName, resume="allow", id = run_id)

    # * collect registered post ids
    historyData= returnTwitterData(project = projectName, id = run_id)
    
    history_ids = []
    for index, item in historyData.iterrows():
        history_ids.append(item['id'])

    
    for data in all_data:
        if(data is not None):
            for item in data:
                # check if miner's response already exists in storage
                if item['id'] in history_ids:
                    continue
                wandb.log({
                    "id": item['id'],
                    "text": item['text'],
                    "url_hash": item['url_hash'],
                    "url": item['url'],
                    "created_at": item['created_at'],
                    "type": item['type']
                })
    run.finish()


# * Returning all data in storage
def returnRedditdata(project = "scraping_subnet-neurons", id = "w8937gls"):
    api = wandb.Api()
    run = api.run(f"aureliojafer/{project}/{id}")
    historyData = run.history()
    return historyData

# output all Reddit data as csv file
def printRedditCSV():
    api = wandb.Api()
    run = api.run("aureliojafer/scraping_subnet-neurons/w8937gls")
    historyData = run.history()

    with open('outputReddit.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file)
        writer.writeheader()
        writer.writerows(historyData)
    return historyData








def returnTwitterData(project = "scraping_subnet-neurons", id = "g1ibv7db"):
    api = wandb.Api()
    run = api.run(f"aureliojafer/{project}/{id}")
    historyData = run.history()
    return historyData



# output all Twitter data as csv file
def printTwitterCSV():
    api = wandb.Api()
    run = api.run("aureliojafer/scraping_subnet-neurons/g1ibv7db")
    historyData = run.history()
    if isinstance(historyData, pd.DataFrame):
        keys = historyData.keys()  # Get column names if historyData is a DataFrame
    else:
        # Handle the case where historyData is not a DataFrame
        keys = historyData.data[0].keys() if hasattr(historyData, 'data') else []
    
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


