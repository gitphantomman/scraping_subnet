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


class ActorConfig:
    def __init__(self, actor_id):
        self.api_key = os.environ.get('APIFY_API_KEY')
        self.actor_id = actor_id


def run_actor(actor_config: ActorConfig, run_input, default_dataset_id="defaultDatasetId"):
    """
        Function to scrape recent posts based on a query.

        Args:
            run_input (dict): The input to the actor.
            default_dataset_id: `defaultDatasetId`
            actor_config (ActorConfig): The configuration to use. Defaults to ApifyConfig().
        Returns:
            None
        """
    client = ApifyClient(actor_config.api_key)
    logger.info("Running actor: {actor_id}".format(actor_id=actor_config.actor_id))
    run = client.actor(actor_config.actor_id).call(run_input=run_input)
    logger.info("Actor run: {run}".format(run=run))

    data_set = []
    for item in client.dataset(run[default_dataset_id]).iterate_items():
        data_set.append(item)

    logger.info("Fetched {count} items from dataset".format(count=len(data_set)))

    return data_set
