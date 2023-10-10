import wandb
# You have to set project name here
run1 = wandb.init(project="scraping_subnet")

print(f'run id: {run1.id}')