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
from neurons.utils import mask_sensitive_data

logger = logging.getLogger(__name__)


class ApifyConfig:
    """Configuration class to hold basic reddit and scraper configurations"""
    # The Apify API key. Default is None
    api_key: str = None
    # Apify actor name
    actor_id: str = None

    def __init__(self):
        self.api_key = os.getenv("APIFY_API_KEY")

    def __str__(self):
        return '''Configuration:
        Api Key: {api_key}
        '''.format(api_key=mask_sensitive_data(self.api_key))


def run_actor(actor_id: str, run_input, default_dataset_id="defaultDatasetId", config=None):
    """
        Function to scrape recent posts based on a query.

        Args:
            actor_id (str): The id of the actor to run.
            run_input (dict): The input to the actor.
            default_dataset_id: `defaultDatasetId`
            config (ApifyConfig): The configuration to use. Defaults to ApifyConfig().
        Returns:
            None
        """

    if config is None:
        config = ApifyConfig()

    client = ApifyClient(config.api_key)

    logger.info("Running actor: {actor_id}".format(actor_id=actor_id))

    run = client.actor(actor_id).call(run_input=run_input)

    logger.info("Actor run: {run}".format(run=run))

    # Fetch and print Actor results from the run's dataset (if there are any)
    data_set = []
    for item in client.dataset(run[default_dataset_id]).iterate_items():
        data_set.append(item)

    logger.info("Fetched {count} items from dataset".format(count=len(data_set)))

    return data_set
