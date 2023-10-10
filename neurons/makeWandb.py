import wandb
run1 = wandb.init(project="scraping_subnet")

print(f'run id: {run1.id}')