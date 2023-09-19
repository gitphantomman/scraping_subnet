import wandb

#Initialize Wandb
def store(data):
    run = wandb.init(project="scraping_subnet-neurons", id = "oyejjkqi")
    for item in data:
        print(item)
        wandb.log({
            "id": item.id,
            "title": item.title,
            "content": item.content,
            "url": item.url,
            "created_utc": item.created_utc
        })
    run.finish()
# api = wandb.Api()

# run = api.run("aureliojafer/scraping_subnet-neurons/oyejjkqi")
# historyData = run.history()
# print(historyData)
