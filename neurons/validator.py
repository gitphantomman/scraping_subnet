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
# dealings in the software.


# Importing necessary libraries and modules
import os
import time
import torch
import argparse
import traceback
import bittensor as bt
import storeWB
import scoreModule
import scraping


# This function is responsible for setting up and parsing command-line arguments.
def get_config():
    """
    This function sets up and parses command-line arguments.
    """
    parser = argparse.ArgumentParser()
    
    # TODO: Validate the wandb run id and project name
    # Adds wandb arguments for storing
    parser.add_argument('--wandb.username', default = 'aureliojafer', help = 'Adds a wandb username to store data')
    parser.add_argument('--wandb.twitter_run_id', default = 'g1ibv7db', help = 'Adds a wandb run id to store twitter scraping data')
    parser.add_argument('--wandb.reddit_run_id', default = 'w8937gls', help = 'Adds a wandb run id to store reddit scraping data')
    parser.add_argument('--wandb.project', default = 'scraping_subnet-neurons', help = 'Adds a wandb project name to store')
    
    # Adds override arguments for network and netuid.
    parser.add_argument( '--netuid', type = int, default = 1, help = "The chain subnet uid." )
    # Adds subtensor specific arguments i.e. --subtensor.chain_endpoint ... --subtensor.network ...
    bt.subtensor.add_args(parser)
    # Adds logging specific arguments i.e. --logging.debug ..., --logging.trace .. or --logging.logging_dir ...
    bt.logging.add_args(parser)
    # Adds wallet specific arguments i.e. --wallet.name ..., --wallet.hotkey ./. or --wallet.path ...
    bt.wallet.add_args(parser)
    # Parse the config (will take command-line arguments if provided)
    # To print help message, run python3 neurons/validator.py --help
    config =  bt.config(parser)

    # Logging is crucial for monitoring and debugging purposes.
    config.full_path = os.path.expanduser(
        "{}/{}/{}/netuid{}/{}".format(
            config.logging.logging_dir,
            config.wallet.name,
            config.wallet.hotkey,
            config.netuid,
            'validator',
        )
    )
    # Ensure the logging directory exists.
    if not os.path.exists(config.full_path): os.makedirs(config.full_path, exist_ok=True)

    # Return the parsed config.
    return config

# Wandb: append data to reddit dataset
def store_Reddit_wandb(all_data, username, projectName, runid):
    """
    This function stores all data from reddit to wandb.
    """
    storeWB.store_reddit(all_data = all_data, username= username, projectName = projectName, run_id = runid)

# Wandb: append data to twitter dataset
def store_Twitter_wandb(all_data, username, projectName, runid):
    """
    This function stores all data from twitter to wandb.
    """
    storeWB.store_twitter(all_data = all_data, username= username, projectName = projectName, run_id = runid)
import random
def main( config ):
    """
    This is the main function that sets up logging, initializes bittensor objects, and starts the validator loop.
    """
    # Set up logging with the provided configuration and directory.
    bt.logging(config=config, logging_dir=config.full_path)
    bt.logging.info(f"Running validator for subnet: {config.netuid} on network: {config.subtensor.chain_endpoint} with config:")
    # Log the configuration for reference.
    bt.logging.info(config)

    # These are core Bittensor classes to interact with the network.
    bt.logging.info("Setting up bittensor objects.")

    # The wallet holds the cryptographic key pairs for the validator.
    wallet = bt.wallet( config = config )
    bt.logging.info(f"Wallet: {wallet}")

    # The subtensor is our connection to the Bittensor blockchain.
    subtensor = bt.subtensor( config = config )
    bt.logging.info(f"Subtensor: {subtensor}")

    # Dendrite is the RPC client; it lets us send messages to other nodes (axons) in the network.
    dendrite = bt.dendrite( wallet = wallet )
    bt.logging.info(f"Dendrite: {dendrite}")

    # The metagraph holds the state of the network, letting us know about other miners.
    metagraph = subtensor.metagraph( config.netuid )
    metagraph.sync(subtensor = subtensor)
    bt.logging.info(f"Metagraph: {metagraph}")

    if wallet.hotkey.ss58_address not in metagraph.hotkeys:
        bt.logging.error(f"\nYour validator: {wallet} if not registered to chain connection: {subtensor} \nRun btcli register and try again.")
        exit()
    else:
        # Each miner gets a unique identity (UID) in the network for differentiation.
        my_subnet_uid = metagraph.hotkeys.index(wallet.hotkey.ss58_address)
        bt.logging.info(f"Running validator on uid: {my_subnet_uid}")

    bt.logging.info("Building validation weights.")

    # Init miner scores and other params
    alpha = 0.9
    scores = torch.ones_like(metagraph.S, dtype=torch.float32)
    bt.logging.info(f"initalScores:{scores}")
    cur_block = subtensor.block
    # scores = scores * metagraph.last_update > cur_block - 10
    bt.logging.info(f"Scores after last update:{scores}")
    scores = scores * (metagraph.total_stake < 1.024e3)
    scores = scores * torch.Tensor([metagraph.neurons[uid].axon_info.ip != '0.0.0.0' for uid in metagraph.uids])
    step = 0
    
    bt.logging.info(f"Weights: {scores}")
    bt.logging.info("Starting validator loop.")
    
    total_dendrites_per_query = 25
    minimum_dendrites_per_query = 3
    # Main loop
    while True:
        # Per 10 blocks, sync the subtensor state with the blockchain.
        if subtensor.block % 10 == 0:
            metagraph.sync(subtensor = subtensor)

        # If the metagraph has changed, update the weights.
        # Get the uids of all miners in the network.
        uids = metagraph.uids.tolist()

        # If there are more uids than scores, add more weights.
        if len(uids) > len(scores):
            bt.logging.trace("Adding more weights")
            size_difference = len(uids) - len(scores)
            new_scores = torch.zeros(size_difference, dtype=torch.float32)
            scores = torch.cat((scores, new_scores))
            del new_scores
        # If there are less uids than scores, remove some weights.
        queryable_uids = (metagraph.total_stake < 1.024e3)
        bt.logging.info(f"queryable_uids:{queryable_uids}")
        
        # Remove the weights of miners that are not queryable.
        queryable_uids = queryable_uids * torch.Tensor([metagraph.neurons[uid].axon_info.ip != '0.0.0.0' for uid in uids])
        active_miners = torch.sum(queryable_uids)
        dendrites_per_query = total_dendrites_per_query

        # if there are no active miners, set active_miners to 1
        if active_miners == 0:
            active_miners = 1
        # if there are less than dendrites_per_query * 3 active miners, set dendrites_per_query to active_miners / 3
        if active_miners < total_dendrites_per_query * 3:
            dendrites_per_query = int(active_miners / 3)
        else:
            dendrites_per_query = total_dendrites_per_query
        
        # less than 3 set to 3
        if dendrites_per_query < minimum_dendrites_per_query:
                dendrites_per_query = minimum_dendrites_per_query
        # zip uids and queryable_uids, filter only the uids that are queryable, unzip, and get the uids
        zipped_uids = list(zip(uids, queryable_uids))
        filtered_uids = list(zip(*filter(lambda x: x[1], zipped_uids)))[0]
        bt.logging.info(f"filtered_uids:{filtered_uids}")
        dendrites_to_query = random.sample( filtered_uids, min( dendrites_per_query, len(filtered_uids) ) )
        bt.logging.info(f"dendrites_to_query:{dendrites_to_query}")
            

        try:
            # Filter metagraph.axons by indices saved in dendrites_to_query list
            filtered_axons = [metagraph.axons[i] for i in dendrites_to_query]
            bt.logging.info(f"filtered_axons: {filtered_axons}")
            # Broadcast a GET_DATA query to filtered miners on the network.
            if (step + 1) % 2 == 1:
                responses = dendrite.query(
                    filtered_axons,
                    # Construct a scraping query.
                    scraping.protocol.TwitterScrap(), # Construct a scraping query.
                    # All responses have the deserialize function called on them before returning.
                    deserialize = True, 
                    timeout = 30
                )                

                

                # Update score
                for i, resp_i in enumerate(responses):
                # Initialize the score of each miner.
                    score = 0
                    # If the miner did not respond, set its score to 0.
                    if resp_i != None:
                        # Evaluate how is the miner's performance.
                        score = scoreModule.twitterScore(resp_i, username= config.wandb.username, project = config.wandb.project, run_id = config.wandb.twitter_run_id)
                        # Update the global score of the miner.
                        # This score contributes to the miner's weight in the network.
                        # A higher weight means that the miner has been consistently responding correctly.
                    scores[dendrites_to_query[i]] = alpha * scores[dendrites_to_query[i]] + (1 - alpha) * score 
                    
                bt.logging.info(f"Scores: {scores}")
                # Store into Wandb
                # check if there is any data
                
                if len(responses) > 0:
                    # store data into wandb
                    store_Twitter_wandb(responses, config.wandb.username, config.wandb.project, config.wandb.twitter_run_id)
                else:
                    print("No data found")
            # Periodically update the weights on the Bittensor blockchain.
            if (step + 1) % 2 == 0:
                responses = dendrite.query(
                    filtered_axons,
                    # Construct a scraping query.
                    scraping.protocol.RedditScrap(), # Construct a scraping query.
                    # All responses have the deserialize function called on them before returning.
                    deserialize = True,
                    timeout = 30 
                )                

                

                # Update score
                for i, resp_i in enumerate(responses):
                # Initialize the score of each miner.
                    score = 0
                    # If the miner did not respond, set its score to 0.
                    if resp_i != None:
                        # Evaluate how is the miner's performance.
                        score = scoreModule.redditScore(resp_i, username= config.wandb.username, project = config.wandb.project, run_id = config.wandb.reddit_run_id)
                        # Update the global score of the miner.
                        # This score contributes to the miner's weight in the network.
                        # A higher weight means that the miner has been consistently responding correctly.
                    scores[dendrites_to_query[i]] = alpha * scores[dendrites_to_query[i]] + (1 - alpha) * score
                    
                bt.logging.info(f"Scores: {scores}")
                # Store into Wandb
                # check if there is any data
                
                if len(responses) > 0:
                    # store data into wandb
                    store_Reddit_wandb(responses, config.wandb.username, config.wandb.project, config.wandb.reddit_run_id)
                else:
                    print("No data found")

                
                
            if (step + 1) % 12 == 0:
                # Adjust the scores based on responses from miners.
                # weights = torch.nn.functional.normalize(scores, p=1.0, dim=0)
                weights = scores / torch.sum(scores)
                bt.logging.info(f"Setting weights: {weights}")
                # Miners with higher scores (or weights) receive a larger share of TAO rewards on this subnet.
                (
                    processed_uids,
                    processed_weights,
                ) = bt.utils.weight_utils.process_weights_for_netuid(
                    uids=metagraph.uids,
                    weights=weights,
                    netuid=config.netuid,
                    subtensor=subtensor
                )
                bt.logging.info(f"Processed weights: {processed_weights}")
                bt.logging.info(f"Processed uids: {processed_uids}")
                result = subtensor.set_weights(
                    netuid = config.netuid, # Subnet to set weights on.
                    wallet = wallet, # Wallet to sign set weights using hotkey.
                    uids = processed_uids, # Uids of the miners to set weights for.
                    weights = processed_weights, # Weights to set for the miners.
                    wait_for_inclusion = True
                )
                if result: bt.logging.success('Successfully set weights.')
                else: bt.logging.error('Failed to set weights.')

            step += 1
            # Resync our local state with the latest state from the blockchain.
            metagraph = subtensor.metagraph(config.netuid)
            # Sleep for a duration equivalent to the block time (i.e., time between successive blocks).
            time.sleep(bt.__blocktime__ * 10)

        # If we encounter an unexpected error, log it for debugging.
        except RuntimeError as e:
            bt.logging.error(e)
            traceback.print_exc()

        # If the user interrupts the program, gracefully exit.
        except KeyboardInterrupt:
            bt.logging.success("Keyboard interrupt detected. Exiting validator.")
            exit()

# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    # Parse the configuration.
    config = get_config()
    # Run the main function.
    main( config )

