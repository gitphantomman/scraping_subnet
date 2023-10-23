"""
This is the main module for the miner. It includes the necessary imports, the configuration setup, and the main function that runs the miner.

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

# Importing necessary libraries and modules
import os
import sys
import time
import argparse
import traceback
import bittensor as bt
import local_db.reddit_db as reddit_db
import local_db.twitter_db as twitter_db
import scraping
from typing import Tuple
import torch
from neurons.apify.queries import get_query, QueryType, QueryProvider
# TODO: Check if all the necessary libraries are installed and up-to-date

def get_config():
    """
    This function initializes the necessary command-line arguments.
    Using command-line arguments allows users to customize various miner settings.
    """
    parser = argparse.ArgumentParser()
    # Adds override arguments for network and netuid.
    parser.add_argument( '--netuid', type = int, default = 1, help = "The chain subnet uid." )
    # Adds subtensor specific arguments i.e. --subtensor.chain_endpoint ... --subtensor.network ...
    bt.subtensor.add_args(parser)
    # Adds logging specific arguments i.e. --logging.debug ..., --logging.trace .. or --logging.logging_dir ...
    bt.logging.add_args(parser)
    # Adds wallet specific arguments i.e. --wallet.name ..., --wallet.hotkey ./. or --wallet.path ...
    bt.wallet.add_args(parser)
    # Adds axon specific arguments i.e. --axon.port ...
    bt.axon.add_args(parser)
    # Activating the parser to read any command-line inputs.
    # To print help message, run python3 neurons/miner.py --help
    config = bt.config(parser)

    # Set up logging directory
    # Logging captures events for diagnosis or understanding miner's behavior.
    config.full_path = os.path.expanduser(
        "{}/{}/{}/netuid{}/{}".format(
            config.logging.logging_dir,
            config.wallet.name,
            config.wallet.hotkey,
            config.netuid,
            'miner',
        )
    )
    # Ensure the directory for logging exists, else create one.
    if not os.path.exists(config.full_path): os.makedirs(config.full_path, exist_ok=True)
    return config

# TODO: Add error handling for when the directory for logging cannot be created

# Main takes the config and starts the miner.
def main( config ):
    """
    This function takes the configuration and starts the miner.
    It sets up the necessary Bittensor objects, attaches the necessary functions to the axon, and starts the main loop.
    """
    twitter_query = get_query(QueryType.TWITTER, QueryProvider.TWEET_FLUSH)
    # Activating Bittensor's logging with the set configurations.
    bt.logging(config=config, logging_dir=config.full_path)
    bt.logging.info(f"Running miner for subnet: {config.netuid} on network: {config.subtensor.chain_endpoint} with config:")

    # This logs the active configuration to the specified logging directory for review.
    bt.logging.info(config)

    # Initialize Bittensor miner objects
    # These classes are vital to interact and function within the Bittensor network.
    bt.logging.info("Setting up bittensor objects.")

    # Wallet holds cryptographic information, ensuring secure transactions and communication.
    wallet = bt.wallet( config = config )
    bt.logging.info(f"Wallet: {wallet}")

    # subtensor manages the blockchain connection, facilitating interaction with the Bittensor blockchain.
    subtensor = bt.subtensor( config = config )
    bt.logging.info(f"Subtensor: {subtensor}")

    # metagraph provides the network's current state, holding state about other participants in a subnet.
    metagraph = subtensor.metagraph(config.netuid)
    bt.logging.info(f"Metagraph: {metagraph}")

    last_updated_block = subtensor.block - 100

    if wallet.hotkey.ss58_address not in metagraph.hotkeys:
        bt.logging.error(f"\nYour miner: {wallet} is not registered to chain connection: {subtensor} \nRun btcli wallet register and try again. ")
        exit()
    else:
        # Each miner gets a unique identity (UID) in the network for differentiation.
        my_subnet_uid = metagraph.hotkeys.index(wallet.hotkey.ss58_address)
        bt.logging.info(f"Running miner on uid: {my_subnet_uid}")

    # Set up miner functionalities
    # The blacklist function decides if a request should be ignored.
    def blacklist_twitter( synapse: scraping.protocol.TwitterScrap ) -> Tuple[bool, str]:
        """
        This function runs before the synapse data has been deserialized (i.e. before synapse.data is available).
        The synapse is instead contructed via the headers of the request. It is important to blacklist
        requests before they are deserialized to avoid wasting resources on requests that will be ignored.
        Below: Check that the hotkey is a registered entity in the metagraph.
        """
        if synapse.dendrite.hotkey not in metagraph.hotkeys:
            # Ignore requests from unrecognized entities.
            bt.logging.trace(f'Blacklisting unrecognized hotkey {synapse.dendrite.hotkey}')
            return True, ""
        # are not validators, or do not have enough stake. This can be checked via metagraph.S
        # and metagraph.validator_permit. You can always attain the uid of the sender via a
        # metagraph.hotkeys.index( synapse.dendrite.hotkey ) call.
        # Otherwise, allow the request to be processed further.
        bt.logging.trace(f'Not Blacklisting recognized hotkey {synapse.dendrite.hotkey}')
        return False, ""

    # The priority function determines the order in which requests are handled.
    # More valuable or higher-priority requests are processed before others.
    def priority_twitter( synapse: scraping.protocol.TwitterScrap ) -> float:
        """
        Miners may recieve messages from multiple entities at once. This function
        determines which request should be processed first. Higher values indicate
        that the request should be processed first. Lower values indicate that the
        request should be processed later.
        Below: simple logic, prioritize requests from entities with more stake.
        """
        caller_uid = metagraph.hotkeys.index( synapse.dendrite.hotkey ) # Get the caller index.
        prirority = float( metagraph.S[ caller_uid ] ) # Return the stake as the priority.
        bt.logging.trace(f'Prioritizing {synapse.dendrite.hotkey} with value: ', prirority)
        return prirority
    def blacklist_reddit( synapse: scraping.protocol.RedditScrap ) -> Tuple[bool, str]:
        """
        This function runs before the synapse data has been deserialized (i.e. before synapse.data is available).
        The synapse is instead contructed via the headers of the request. It is important to blacklist
        requests before they are deserialized to avoid wasting resources on requests that will be ignored.
        Below: Check that the hotkey is a registered entity in the metagraph.
        """
        if synapse.dendrite.hotkey not in metagraph.hotkeys:
            # Ignore requests from unrecognized entities.
            bt.logging.trace(f'Blacklisting unrecognized hotkey {synapse.dendrite.hotkey}')
            return True, ""
        # are not validators, or do not have enough stake. This can be checked via metagraph.S
        # and metagraph.validator_permit. You can always attain the uid of the sender via a
        # metagraph.hotkeys.index( synapse.dendrite.hotkey ) call.
        # Otherwise, allow the request to be processed further.
        bt.logging.trace(f'Not Blacklisting recognized hotkey {synapse.dendrite.hotkey}')
        return False, ""

    # The priority function determines the order in which requests are handled.
    # More valuable or higher-priority requests are processed before others.
    def priority_reddit( synapse: scraping.protocol.RedditScrap ) -> float:
        """
        Miners may recieve messages from multiple entities at once. This function
        determines which request should be processed first. Higher values indicate
        that the request should be processed first. Lower values indicate that the
        request should be processed later.
        Below: simple logic, prioritize requests from entities with more stake.
        """
        caller_uid = metagraph.hotkeys.index( synapse.dendrite.hotkey ) # Get the caller index.
        prirority = float( metagraph.S[ caller_uid ] ) # Return the stake as the priority.
        bt.logging.trace(f'Prioritizing {synapse.dendrite.hotkey} with value: ', prirority)
        return prirority

    def twitterScrap( synapse: scraping.protocol.TwitterScrap) -> scraping.protocol.TwitterScrap: 
        """
        This function runs after the TwitterScrap synapse has been deserialized (i.e. after synapse.data is available).
        This function runs after the blacklist and priority functions have been called.
        """
        bt.logging.info(f"number of required data: {synapse.scrap_input} \n")
        tweets = twitter_query.execute(synapse.scrap_input["search_key"])
        synapse.scrap_output = tweets
        bt.logging.info(f"✅ success: number of response data: {len(synapse.scrap_output)} \n")
        return synapse
    
    def redditScrap( synapse: scraping.protocol.RedditScrap) -> scraping.protocol.RedditScrap: 
        """
        This function runs after the RedditScrap synapse has been deserialized (i.e. after synapse.data is available).
        This function runs after the blacklist and priority functions have been called.
        """
        bt.logging.info(f"number of required data: {synapse.scrap_input} \n")
        # Fetch latest N posts from miner's local database.
        fetched_data = reddit_db.fetch_latest_posts(500)
        synapse.scrap_output = fetched_data
        bt.logging.info(f"number of response data: {len(synapse.scrap_output)} \n")
        return synapse

    # Build and link miner functions to the axon.
    # The axon handles request processing, allowing validators to send this process requests.
    
    axon = bt.axon( wallet = wallet, port = config.axon.port )
    bt.logging.info(f"Axon {axon}")

    # Attach determiners which functions are called when servicing a request.
    bt.logging.info(f"Attaching forward function to axon.")
    axon.attach(forward_fn = redditScrap).attach(
        forward_fn = twitterScrap,
        # blacklist_fn = blacklist_twitter,
        # priority_fn = priority_twitter,
    )

    # Serve passes the axon information to the network + netuid we are hosting on.
    # This will auto-update if the axon port of external ip have changed.
    bt.logging.info(f"Serving axon {redditScrap, twitterScrap} on network: {config.subtensor.chain_endpoint} with netuid: {config.netuid}")
    axon.serve( netuid = config.netuid, subtensor = subtensor )

    # Start  starts the miner's axon, making it active on the network.
    bt.logging.info(f"Starting axon server on port: {config.axon.port}")
    axon.start()

    # Keep the miner alive
    # This loop maintains the miner's operations until intentionally stopped.
    bt.logging.info(f"Starting main loop")
    step = 0
    while True:          
        try:
            if subtensor.block - last_updated_block >= 100:
                bt.logging.trace(f"Setting miner weight")
                # find the uid that matches config.wallet.hotkey [meta.axons[N].hotkey == config.wallet.hotkey]
                # set the weight of that uid to 1.0
                uid = None
                try:
                    for _uid, axon in enumerate(metagraph.axons):
                        if axon.hotkey == wallet.hotkey.ss58_address:
                            # uid = axon.uid
                            # uid doesnt exist ona xon
                            uid = _uid
                            break
                    if uid is not None:
                        # 0 weights for all uids
                        weights = torch.Tensor([0.0] * len(metagraph.uids))
                        # 1 weight for uid
                        weights[uid] = 1.0
                        (uids, processed_weights) = bt.utils.weight_utils.process_weights_for_netuid( uids = metagraph.uids, weights = weights, netuid=config.netuid, subtensor = subtensor)
                        subtensor.set_weights(wallet = wallet, netuid = config.netuid, weights = processed_weights, uids = uids)
                        last_updated_block = subtensor.block
                        bt.logging.trace("Miner weight set!")
                    else:
                        bt.logging.warning(f"Could not find uid with hotkey {config.wallet.hotkey} to set weight")
                except Exception as e:
                    bt.logging.warning(f"Could not set miner weight: {e}")
                    raise e
            # Below: Periodically update our knowledge of the network graph.
            if step % 5 == 0:
                metagraph = subtensor.metagraph(config.netuid)
                log =  (f'Step:{step} | '\
                        f'Block:{metagraph.block.item()} | '\
                        f'Stake:{metagraph.S[my_subnet_uid]} | '\
                        f'Rank:{metagraph.R[my_subnet_uid]} | '\
                        f'Trust:{metagraph.T[my_subnet_uid]} | '\
                        f'Consensus:{metagraph.C[my_subnet_uid] } | '\
                        f'Incentive:{metagraph.I[my_subnet_uid]} | '\
                        f'Emission:{metagraph.E[my_subnet_uid]}')
                bt.logging.info(log)
            step += 1
            time.sleep(1)

        # If someone intentionally stops the miner, it'll safely terminate operations.
        except KeyboardInterrupt:
            axon.stop()
            bt.logging.success('Miner killed by keyboard interrupt.')
            break
        # In case of unforeseen errors, the miner will log the error and continue operations.
        except Exception as e:
            bt.logging.error(traceback.format_exc())
            continue


# This is the main function, which runs the miner.
if __name__ == "__main__":
    try:
        main( get_config() )
    except Exception as e:
        bt.logging.error(f"Failed to start the miner due to: {str(e)}")
        sys.exit(1)
