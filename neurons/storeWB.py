import wandb

# * Store all responses from all miners to wandb
def store(all_data, projectName, run_id):

    run = wandb.init(project = projectName, id = run_id)
    print("run_id:", run.id)
    for data in all_data:
        if(data is not None):
            for item in data:
                # print(item)
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
def returnLog():
    api = wandb.Api()
    run = api.run("aureliojafer/scraping_subnet-neurons/zhjgapym")
    historyData = run.history()
    return historyData


