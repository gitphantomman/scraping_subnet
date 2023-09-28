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
    parser.add_argument('--wandb.runid', default = 'g1ibv7db', help = 'Adds a wandb run id to store')
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
    # TODO: Handle error if directory creation fails
    if not os.path.exists(config.full_path): os.makedirs(config.full_path, exist_ok=True)

    # Return the parsed config.
    return config

# Wandb: append data to reddit dataset
def store_reddit_wandb(all_data, projectName, runid):
    """
    This function stores all data from reddit to wandb.
    """
    storeWB.store_reddit(all_data = all_data, projectName = projectName, run_id = runid)

# Wandb: append data to twitter dataset
def store_Twitter_wandb(all_data, projectName, runid):
    """
    This function stores all data from twitter to wandb.
    """
    storeWB.store_twitter(all_data = all_data, projectName = projectName, run_id = runid)

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
    step = 0
    # TODO: Have to change data_per_step or none
    data_per_step = 50
    
    bt.logging.info(f"Weights: {scores}")
    bt.logging.info("Starting validator loop.")
    
    # Main loop
    while True:
        try:
            # Periodically update the weights on the Bittensor blockchain.
            if (step + 1) % 2 == 0:
                # ? Broadcast a GET_DATA query to all miners on the network.
                responses = dendrite.query(
                    metagraph.axons,
                    # Construct a scraping query.
                    scraping.protocol.TwitterScrap( scrap_input = data_per_step ), # Construct a scraping query.
                    # All responses have the deserialize function called on them before returning.
                    deserialize = True, 
                )                

                # ! Store into Wandb
                store_Twitter_wandb(responses, config.wandb.project, config.wandb.runid)
                
                # Update score
                for i, resp_i in enumerate(responses):
                # Initialize the score for the current miner's response.
                    score = 0
                    # Evaluate how is the miner's performance.
                    # ? Calulate each miner's score
                    score = scoreModule.twitterScore(resp_i)
                    # Update the global score of the miner.
                    # This score contributes to the miner's weight in the network.
                    # A higher weight means that the miner has been consistently responding correctly.
                    scores[i] = alpha * scores[i] + (1 - alpha) * score



                # Adjust the scores based on responses from miners.
                weights = torch.nn.functional.normalize(scores, p=1.0, dim=0)
                # ! Bug fix on maxWeightExceed
                bt.logging.info(f"Setting weights: {weights}")
                # Miners with higher scores (or weights) receive a larger share of TAO rewards on this subnet.
                result = subtensor.set_weights(
                    netuid = config.netuid, # Subnet to set weights on.
                    wallet = wallet, # Wallet to sign set weights using hotkey.
                    uids = metagraph.uids, # Uids of the miners to set weights for.
                    weights = weights, # Weights to set for the miners.
                    wait_for_inclusion = True
                )
                if result: bt.logging.success('Successfully set weights.')
                else: bt.logging.error('Failed to set weights.')

            else:
                # ? Broadcast CHECK_MINER query to all miners on the network.
                responses = dendrite.query(
                    metagraph.axons,
                    # Construct a checking query.
                    scraping.protocol.CheckMiner( check_url_hash = "4744c2327123a4025dbe40cf943bf9b2293858f57f7a278c06875c66427e4787" ), # Construct a checking query.
                    # All responses have the deserialize function called on them before returning.
                    deserialize = True, 
                )
                responses_urls = []
                for response in responses:
                    if(response == None): 
                        responses_urls.append('NONE')
                    else:
                        responses_urls.append(response['url'])
                
                new_scores = scoreModule.checkScore(responses_urls)
                # update global miners score.
                for i in range(0, len(responses)):
                    scores[i] = alpha * scores[i] + (1 - alpha) * ( new_scores[i])
                
                # Log the results for monitoring purposes.
                bt.logging.info(f"Received checking responses: {responses}")
                bt.logging.info(f"new score by checking: {scores}")


            # End the current step and prepare for the next iteration.
            step += 1
            # Resync our local state with the latest state from the blockchain.
            metagraph = subtensor.metagraph(config.netuid)
            # Sleep for a duration equivalent to the block time (i.e., time between successive blocks).
            time.sleep(bt.__blocktime__)

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

