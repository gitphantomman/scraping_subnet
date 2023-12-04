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
import scraping
import json
import score.reddit_score
import score.twitter_score
import storage.store
from apify_client import ApifyClient

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


import random

def random_line(a_file="keywords.txt"):
    if not os.path.exists(a_file):
        print(f"Keyword file not found at location: {a_file}")
        quit()
    lines = open(a_file).read().splitlines()
    return random.choice(lines)

def main( config ):
    """
    This is the main function that sets up logging, initializes bittensor objects, and starts the validator loop.
    """
    # Set up logging with the provided configuration and directory.
    bt.logging(config=config, logging_dir=config.full_path)
    bt.logging.info(f"Running validator for subnet: {config.netuid} on network: {config.subtensor.chain_endpoint} with config:")
    # Log the configuration for reference.
    bt.logging.info(config)

    # Check access to Apify
    try:
        client = ApifyClient(os.getenv("APIFY_API_KEY"))
        client.actors().list()
    except Exception as e:
        bt.logging.error(f"{e}")
        bt.logging.error(f"Unable to connect to Apify. Check your dotenv file and make sure your APIFY_API_KEY is set correctly.")
        exit()

    # Check access to storage
    try:
        storage.store.s3.Bucket('twitterscrapingbucket').Acl().owner
    except Exception as e:
        bt.logging.error(f"{e}")
        bt.logging.error(f"Unable to connect to wasabi storage. Check your dotenv file and make sure your WASABI_ACCESS_KEY_ID, WASABI_ACCESS_KEY, and INDEXING_API_KEY are set correctly.")
        exit()

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
    redditAlpha = 0.7
    twitterAlpha = 0.7

    # Restore weights, or initialize weights for each miner to 0.
    scores_file = "scores.pt"
    try:
        scores = torch.load(scores_file)
        bt.logging.info(f"Loaded scores from save file: {scores}")
    except:
        scores = torch.zeros_like(metagraph.S, dtype=torch.float32)
        bt.logging.info(f"Initialized all scores to 0")


    curr_block = subtensor.block

    # all nodes with more than 1e3 total stake are set to 0 (sets validators weights to 0)

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
            bt.logging.info(f"🔄 Syncing metagraph with subtensor.")

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
        queryable_uids = (metagraph.total_stake >= 0)
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
            if step % 4 == 0:
                search_key = random_line()
                bt.logging.info(f"\033[92m 𝕏 ⏩ Sending tweeter query ({search_key}). \033[0m")
                responses = dendrite.query(
                    filtered_axons,
                    # Construct a scraping query.
                    scraping.protocol.TwitterScrap(scrap_input = {"search_key" : [search_key]}), # Construct a scraping query.
                    # All responses have the deserialize function called on them before returning.
                    deserialize = True, 
                    timeout = 60
                )

                # Update score
                new_scores = []
                try:
                    if(len(responses) > 0 and responses is not None):
                        new_scores = score.twitter_score.calculateScore(responses = responses, tag = search_key)
                        bt.logging.info(f"✅ new_scores: {new_scores}")
                except Exception as e:
                    bt.logging.error(f"❌ Error in twitterScore: {e}")
                for i, score_i in enumerate(new_scores):
                    scores[dendrites_to_query[i]] = twitterAlpha * scores[dendrites_to_query[i]] + (1 - twitterAlpha) * score_i
                bt.logging.info(f"\033[92m ✓ Updated Scores: {scores} \033[0m")
                
                try:
                    if len(responses) > 0:
                        indexing_result = storage.store.twitter_store(data = responses, search_keys=[search_key])
                        bt.logging.info(f"\033[92m saving index info: {indexing_result} \033[0m")
                    else:
                        bt.logging.warning("\033[91m ⚠ No twitter data found in responses \033[0m")
                except Exception as e:
                    bt.logging.error(f"❌ Error in store_Twitter: {e}")

                    
                        
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
                    if result: bt.logging.success('✅ Successfully set weights.')
                    else: bt.logging.error('Failed to set weights.')

            # Periodically update the weights on the Bittensor blockchain.
            if step % 4 == 2:
                bt.logging.info(f"\033[92m ᕕ ⏩ Sending reddit query. \033[0m")
                search_key = random_line()
                responses = dendrite.query(
                    filtered_axons,
                    # Construct a scraping query.
                    scraping.protocol.RedditScrap(scrap_input = {"search_key" : [search_key]}), # Construct a scraping query.
                    # All responses have the deserialize function called on them before returning.
                    deserialize = True,
                    timeout = 60 
                )

                # Update score
                new_scores = []
                try:
                    if(len(responses) > 0 and responses is not None):
                        new_scores = score.reddit_score.calculateScore(responses = responses, tag = search_key)
                        # bt.logging.info(f"✅ new_scores: {new_scores}")
                except Exception as e:
                    bt.logging.error(f"❌ Error in redditScore: {e}")
                for i, score_i in enumerate(new_scores):
                    scores[dendrites_to_query[i]] = redditAlpha * scores[dendrites_to_query[i]] + (1 - redditAlpha) * score_i
                bt.logging.info(f"\033[92m ✓ Updated Scores: {scores} \033[0m")
                try:
                    if len(responses) > 0:
                        indexing_result = storage.store.reddit_store(data = responses, search_keys=[search_key])
                        bt.logging.info(f"\033[92m saving index info: {indexing_result} \033[0m")
                    else:
                        bt.logging.warning("\033[91m ⚠ No reddit data found in responses \033[0m")
                except Exception as e:
                    bt.logging.error(f"❌ Error in store_reddit: {e}")            
                
                # If the metagraph has changed, update the weights.
                # Adjust the scores based on responses from miners.
                # weights = torch.nn.functional.normalize(scores, p=1.0, dim=0)
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
                    if result: bt.logging.success('✅ Successfully set weights.')
                    else: bt.logging.error('Failed to set weights.')

            step += 1

            if last_reset_weights_block + 1800 < current_block:
                bt.logging.trace(f"Clearing weights for validators and nodes without IPs")
                last_reset_weights_block = current_block

                
                # set all nodes without ips set to 0
                scores = scores * torch.Tensor([metagraph.neurons[uid].axon_info.ip != '0.0.0.0' for uid in metagraph.uids])

            # Resync our local state with the latest state from the blockchain.
            metagraph = subtensor.metagraph(config.netuid)
            torch.save(scores, scores_file)
            bt.logging.info(f"Saved weights to \"{scores_file}\"")
            # Sleep for a duration equivalent to the block time (i.e., time between successive blocks).
            time.sleep(bt.__blocktime__ * 10)

        # If we encounter an unexpected error, log it for debugging.
        except RuntimeError as e:
            bt.logging.error(e)
            traceback.print_exc()
        except Exception as e:
            bt.logging.error(e)
            continue
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

