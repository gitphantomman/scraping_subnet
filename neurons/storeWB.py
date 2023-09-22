import wandb
import csv
# * Store all responses from all miners to wandb
def store(all_data, projectName, run_id):

    run = wandb.init(project = projectName,  resume="allow",  id = run_id)

    # * collect registered ids
    historyData= returnData(project = projectName, id = run_id)
    history_ids = []
    for item in historyData:
        history_ids.append(item['id'])
    for data in all_data:
        if(data is not None):
            for item in data:
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



# * Testing
def returnData(project, id):
    api = wandb.Api()
    run = api.run(f"aureliojafer/{project}/{id}")
    historyData = run.history()
    return historyData


def returnLog():
    api = wandb.Api()
    run = api.run("aureliojafer/scraping_subnet-neurons/w8937gls")
    historyData = run.history()
    print(len(historyData))
    # historyData.to_csv("output.csv", index = False)
    keys = historyData[0].keys()
    with open('output.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(historyData)
    return historyData
returnLog()


