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

import os
import logging
from apify_client import ApifyClient, ApifyClientAsync

# Set up logger for the script
logger = logging.getLogger(__name__)

from dotenv import load_dotenv

load_dotenv()
class ActorConfig:
    """
    Configuration class for actors in Apify.
    """
    def __init__(self, actor_id: str):
        """
        Initialize the actor configuration with API key and actor ID.

        Args:
            actor_id (str): The ID of the actor.
        """
        # self.api_key = os.environ.get('APIFY_API_KEY')  # Get the Apify API key from environment variable
        self.api_key = os.getenv("APIFY_API_KEY")
        self.actor_id = actor_id  # Actor ID
        self.timeout_secs = 30
        self.memory_mbytes = None 


def run_actor(actor_config: ActorConfig, run_input: dict, default_dataset_id: str = "defaultDatasetId"):
    """
    Run an actor in Apify and fetch the resulting data.

    Args:
        actor_config (ActorConfig): The configuration to use for running the actor.
        run_input (dict): The input parameters for the actor run.
        default_dataset_id (str, optional): ID of the dataset to fetch data from. Defaults to "defaultDatasetId".

    Returns:
        list[dict]: List of items fetched from the dataset.
    """
    # Initialize the Apify client with the API key
    client = ApifyClient(actor_config.api_key)
    logger.info(f"Running actor: {actor_config.actor_id}")
    
     # Start the actor run
    run = client.actor(actor_config.actor_id).call(run_input=run_input, 
                                                   timeout_secs=actor_config.timeout_secs, 
                                                   memory_mbytes=actor_config.memory_mbytes)
    logger.info(f"Actor run: {run}")

    # Fetch data items from the specified dataset
    data_set = [item for item in client.dataset(run[default_dataset_id]).iterate_items()]

    logger.info(f"Fetched {len(data_set)} items from dataset")
    return data_set

async def run_actor_async(actor_config: ActorConfig, run_input: dict, default_dataset_id: str = "defaultDatasetId"):
    """
    Run an actor in Apify and fetch the resulting data.

    Args:
        actor_config (ActorConfig): The configuration to use for running the actor.
        run_input (dict): The input parameters for the actor run.
        default_dataset_id (str, optional): ID of the dataset to fetch data from. Defaults to "defaultDatasetId".

    Returns:
        list[dict]: List of items fetched from the dataset.
    """
    # Initialize the Apify client with the API key
    client = ApifyClientAsync(actor_config.api_key)
    logger.info(f"Running actor: {actor_config.actor_id}")
    run = await client.actor(actor_config.actor_id).call(run_input=run_input, timeout_secs=actor_config.timeout_secs, memory_mbytes=actor_config.memory_mbytes)  # Start the actor run
    logger.info(f"Actor run: {run}")

    # Fetch data items from the specified dataset
    dataset = client.dataset(run[default_dataset_id])
    items = dataset.iterate_items()

    fetched_items = []

    async for item in items:
        fetched_items.append(item)

    logger.info(f"Fetched {len(fetched_items)} items from dataset")
    return fetched_items
