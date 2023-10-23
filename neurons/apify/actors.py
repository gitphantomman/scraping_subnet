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
from apify_client import ApifyClient

# Set up logger for the script
logger = logging.getLogger(__name__)


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
        self.api_key = os.environ.get('APIFY_API_KEY')  # Get the Apify API key from environment variable
        self.actor_id = actor_id  # Actor ID


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
    run = client.actor(actor_config.actor_id).call(run_input=run_input)  # Start the actor run
    logger.info(f"Actor run: {run}")

    # Fetch data items from the specified dataset
    data_set = [item for item in client.dataset(run[default_dataset_id]).iterate_items()]

    logger.info(f"Fetched {len(data_set)} items from dataset")
    return data_set
