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
import json
from new_score import calculateScore

# This function is responsible for setting up and parsing command-line arguments.
def get_config():
    """
    This function sets up and parses command-line arguments.
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
def store_Reddit_wandb(all_data, username, projectName, run_id):
    """
    This function stores all data from reddit to wandb.
    """
    storeWB.store_reddit(all_data = all_data, username= username, projectName = projectName, run_id = run_id)

# Wandb: append data to twitter dataset
def store_Twitter_wandb(all_data, username, projectName, run_id):
    """
    This function stores all data from twitter to wandb.
    """
    storeWB.store_twitter(all_data = all_data, username= username, projectName = projectName, run_id = run_id)

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

    # Initialize alpha for reddit and twitter
    redditAlpha = 0.9
    twitterAlpha = 0.8

    # Initialize weights for each miner to 1.
    scores = torch.ones_like(metagraph.S, dtype=torch.float32)
    bt.logging.info(f"inital miner scores:{scores}")

    
    curr_block = subtensor.block

    # all nodes with more than 1e3 total stake are set to 0 (sets validtors weights to 0)
    scores = scores * (metagraph.total_stake < 1.024e3)
    # set all nodes without ips set to 0
    scores = scores * torch.Tensor([metagraph.neurons[uid].axon_info.ip != '0.0.0.0' for uid in metagraph.uids])
    step = 0
    
    

    bt.logging.info(f"Initial scores: {scores}")
    bt.logging.info("Starting validator loop.")
    
    total_dendrites_per_query = 25
    minimum_dendrites_per_query = 3
    last_updated_block = curr_block - (curr_block % 100)
    last_reset_weights_block = curr_block

    
    

    # Main loop
    while True:
        # Per 10 blocks, sync the subtensor state with the blockchain.
        if step % 5 == 0:
            metagraph.sync(subtensor = subtensor)
            bt.logging.info(f"Syncing metagraph with subtensor.")

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
            
        
        # every 2 minutes, query the miners
        try:
            # Filter metagraph.axons by indices saved in dendrites_to_query list
            filtered_axons = [metagraph.axons[i] for i in dendrites_to_query]
            bt.logging.info(f"filtered_axons: {filtered_axons}")
            # Broadcast a GET_DATA query to filtered miners on the network.

            # * every 10 minutes, query the miners for twitter data
            if (step + 1) % 2 == 1:
                responses = dendrite.query(
                    filtered_axons,
                    # Construct a scraping query.
                    scraping.protocol.TwitterScrap(scrap_input = {"search_key" : ["bittensor"]}), # Construct a scraping query.
                    # All responses have the deserialize function called on them before returning.
                    deserialize = True, 
                    timeout = 30
                )              
                if(len(responses) > 0):
                    for item in responses:
                        bt.logging.info(f"✅ Length of Responses: {len(item)}")
                

                # Update score
                new_scores = []
                try:
                    if(len(responses) > 0 and responses is not None):
                        new_scores = calculateScore(responses = responses, tag = "bittensor")
                        bt.logging.info(f"✅ new_scores: {new_scores}")
                except Exception as e:
                    bt.logging.error(f"❌ Error in twitterScore: {e}")
                for i, score_i in enumerate(new_scores):
                    scores[dendrites_to_query[i]] = twitterAlpha * scores[dendrites_to_query[i]] + (1 - twitterAlpha) * score_i
                bt.logging.info(f"✅ Updated Scores: {scores}")
                
                # Store 

                # # check if there is any data
                # try:
                #     if len(responses) > 0:
                #         # store data into wandb
                #         store_Twitter_wandb(responses, config.wandb.username, config.wandb.project, wandb_params['twitter'])
                #     else:
                #         bt.logging.warning("No twitter data found in responses")
                # except Exception as e:
                #     bt.logging.error(f"Error in store_Twitter_wandb: {e}")
                    
                        
                current_block = subtensor.block
                if current_block - last_updated_block > 100:
                    
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
                    )
                    last_updated_block = current_block
                    if result: bt.logging.success('Successfully set weights.')
                    else: bt.logging.error('Failed to set weights.')
                if last_reset_weights_block + 1800 < current_block:

                    bt.logging.trace(f"Resetting weights")
                    scores = torch.ones_like( metagraph.uids , dtype = torch.float32 )
                    last_reset_weights_block = current_block
                    # scores = scores * metagraph.last_update > current_block - 600

                    # all nodes with more than 1e3 total stake are set to 0 (sets validtors weights to 0)
                    scores = scores * (metagraph.total_stake < 1.024e3) 

                    # set all nodes without ips set to 0
                    scores = scores * torch.Tensor([metagraph.neurons[uid].axon_info.ip != '0.0.0.0' for uid in metagraph.uids])
            # Periodically update the weights on the Bittensor blockchain.
            # if (step + 1) % 3 == 1:
            #     responses = dendrite.query(
            #         filtered_axons,
            #         # Construct a scraping query.
            #         scraping.protocol.RedditScrap(), # Construct a scraping query.
            #         # All responses have the deserialize function called on them before returning.
            #         deserialize = True,
            #         timeout = 30 
            #     )

            #     # Update score
            #     try:
            #         for i, resp_i in enumerate(responses):
            #         # Initialize the score of each miner.
            #             score = 0
            #             # If the miner did not respond, set its score to 0.
            #             if resp_i != None:
            #                 # Evaluate how is the miner's performance.
            #                 score = scoreModule.redditScore(resp_i, username= config.wandb.username, project = config.wandb.project, run_id = wandb_params['reddit'])
            #                 # Update the global score of the miner.
            #                 # This score contributes to the miner's weight in the network.
            #                 # A higher weight means that the miner has been consistently responding correctly.
            #             scores[dendrites_to_query[i]] = redditAlpha * scores[dendrites_to_query[i]] + (1 - redditAlpha) * score
            #     except Exception as e:
            #         bt.logging.error(f"Error in redditScore: {e}")

            #     bt.logging.info(f"Scores: {scores}")
            #     # Store into Wandb
            #     # check if there is any data
            #     try:
            #         if len(responses) > 0:
            #             # store data into wandb
            #             store_Reddit_wandb(responses, config.wandb.username, config.wandb.project, wandb_params['reddit'])
            #         else:
            #             print("No data found")
            #     except Exception as e:
            #         bt.logging.error(f"Error in store_Reddit_wandb: {e}")                
                
            #     # If the metagraph has changed, update the weights.
            #     # Adjust the scores based on responses from miners.
            #     # weights = torch.nn.functional.normalize(scores, p=1.0, dim=0)
            #     current_block = subtensor.block
            #     if current_block - last_updated_block > 100:
                    
            #         weights = scores / torch.sum(scores)
            #         bt.logging.info(f"Setting weights: {weights}")
            #         # Miners with higher scores (or weights) receive a larger share of TAO rewards on this subnet.
            #         (
            #             processed_uids,
            #             processed_weights,
            #         ) = bt.utils.weight_utils.process_weights_for_netuid(
            #             uids=metagraph.uids,
            #             weights=weights,
            #             netuid=config.netuid,
            #             subtensor=subtensor
            #         )
            #         bt.logging.info(f"Processed weights: {processed_weights}")
            #         bt.logging.info(f"Processed uids: {processed_uids}")
            #         result = subtensor.set_weights(
            #             netuid = config.netuid, # Subnet to set weights on.
            #             wallet = wallet, # Wallet to sign set weights using hotkey.
            #             uids = processed_uids, # Uids of the miners to set weights for.
            #             weights = processed_weights, # Weights to set for the miners.
            #         )
            #         last_updated_block = current_block
            #         if result: bt.logging.success('Successfully set weights.')
            #         else: bt.logging.error('Failed to set weights.')
            #     if last_reset_weights_block + 1800 < current_block:

            #         bt.logging.trace(f"Resetting weights")
            #         scores = torch.ones_like( metagraph.uids , dtype = torch.float32 )
            #         last_reset_weights_block = current_block
            #         # scores = scores * metagraph.last_update > current_block - 600

            #         # all nodes with more than 1e3 total stake are set to 0 (sets validtors weights to 0)
            #         scores = scores * (metagraph.total_stake < 1.024e3) 

            #         # set all nodes without ips set to 0
            #         scores = scores * torch.Tensor([metagraph.neurons[uid].axon_info.ip != '0.0.0.0' for uid in metagraph.uids])
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

