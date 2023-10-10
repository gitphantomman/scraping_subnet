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

# am4ybwqi
# ga3vulxa
# GET request returning all the Twitter data from wandb
@app.get("/twitter")
def read_twitter_data(from_: Optional[int] = 0, limit: Optional[int] = 10):
    # Get the data from wandb, sort it by date, limit to 'limit' and return as array
    api = wandb.Api()
    run = api.run("aureliojafer/scraping_subnet-neurons/am4ybwqi")
    historyData = run.history()
    print(historyData)
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
    run = api.run("aureliojafer/scraping_subnet-neurons/am4ybwqi")
    historyData = run.history()
    # Sort by date and limit to 'limit'
    dataArray = historyData.values
    return len(dataArray)


# GET request returning all the Reddit data from wandb
@app.get("/reddit")
def read_twitter_data(from_: Optional[int] = 0, limit: Optional[int] = 10):
    # Get the data from wandb, sort it by date, limit to 'limit' and return as array
    api = wandb.Api()
    run = api.run("aureliojafer/scraping_subnet-neurons/ga3vulxa")
    historyData = run.history()
    # Sort by date and limit to 'limit'
    sortedData = historyData.sort_values(by='created_at', ascending=False).iloc[from_:from_+limit]
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
    run = api.run("aureliojafer/scraping_subnet-neurons/ga3vulxa")
    historyData = run.history()
    # Sort by date and limit to 'limit'
    dataArray = historyData.values
    return len(dataArray)

@app.get("/api/v1/getTwitterData")
def getTwitterData():
    api = wandb.Api()
    run = api.run("aureliojafer/scraping_subnet-neurons/am4ybwqi")
    historyData = run.history()
    # Sort by date and limit to 'limit'
    sortedData = historyData.sort_values(by='created_at', ascending=False)
    # Convert dataframe to array
    dataArray = sortedData.values
    return dataArray.tolist()

