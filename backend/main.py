# FastAPI app template for backend
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import wandb
from typing import Optional
app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

# GET request returning all the Twitter data from wandb
@app.get("/twitter")
def read_twitter_data(from_: Optional[int] = 0, limit: Optional[int] = 10):
    # Get the data from wandb, sort it by date, limit to 'limit' and return as array
    api = wandb.Api()
    run = api.run("aureliojafer/scraping_subnet-neurons/g1ibv7db")
    historyData = run.history()
    # Sort by date and limit to 'limit'
    sortedData = historyData.sort_values(by='created_at', ascending=False).iloc[from_:from_+limit]
    # Convert dataframe to array
    dataArray = sortedData.values
    return dataArray.tolist()

# GET request returning number of twitter data points
@app.get("/twitter/length")
def read_twitter_data_length():
    # Get the data from wandb, sort it by date, limit to 'limit' and return as array
    api = wandb.Api()
    run = api.run("aureliojafer/scraping_subnet-neurons/g1ibv7db")
    historyData = run.history()
    # Sort by date and limit to 'limit'
    dataArray = historyData.values
    return len(dataArray)


# GET request returning all the Reddit data from wandb
@app.get("/reddit")
def read_twitter_data(from_: Optional[int] = 0, limit: Optional[int] = 10):
    # Get the data from wandb, sort it by date, limit to 'limit' and return as array
    api = wandb.Api()
    run = api.run("aureliojafer/scraping_subnet-neurons/w8937gls")
    historyData = run.history()
    # Sort by date and limit to 'limit'
    sortedData = historyData.sort_values(by='created_utc', ascending=False).iloc[from_:from_+limit]
    print(sortedData)
    # Convert dataframe to array
    dataArray = sortedData.values
    # print column titles
    return dataArray.tolist()


# GET request returning number of reddit data points
@app.get("/reddit/length")
def read_twitter_data_length():
    # Get the data from wandb, sort it by date, limit to 'limit' and return as array
    api = wandb.Api()
    run = api.run("aureliojafer/scraping_subnet-neurons/w8937gls")
    historyData = run.history()
    # Sort by date and limit to 'limit'
    dataArray = historyData.values
    return len(dataArray)

