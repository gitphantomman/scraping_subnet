
<div align="center">

# **Scraping Subnet** <!-- omit in toc -->
[![Discord Chat](https://img.shields.io/discord/308323056592486420.svg)](https://discord.gg/bittensor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 

---

### The Incentivized Internet <!-- omit in toc -->

[Discord](https://discord.gg/bittensor) • [Network](https://taostats.io/) • [Research](https://bittensor.com/whitepaper)

</div>

---

This repo contains all the necessary files and functions to define Scraping subnet incentive mechanisms. You can run this project in three ways,
on Bittensor's main-network (real TAO, to be released), Bittensor's test-network (fake TAO), or with your own staging-network. This repo includes instructions for doing all three.

# Introduction

Data scraping plays a pivotal role in many AI and machine learning models, often serving as the partial layer for various subnets, including s1. We aim to extract data from platforms like Reddit, Twitter, and other social media sites, consolidating this information into shared storage solutions like Weights & Biases (wandb). In the future, we plan to utilize the storage subnet of Bittensor to enhance our data storage capabilities. 

![Alt text](docs/Screenshot_18.png)




- `scraping/protocol.py`: The file where the wire-protocol used by miners and validators is defined.
- `neurons/miner.py`: This script which defines the miner's behavior, i.e., how the miner responds to requests from validators.
- `neurons/validator.py`: This script which defines the validator's behavior, i.e., how the validator requests information from miners and determines scores.

</div>



---

# Installation
This repository requires python3.8 or higher. To install, simply clone this repository and install the requirements.
```bash
git clone https://github.com/gitphantomman/scraping_subnet.git
cd scraping_subnet
python -m pip install -r requirements.txt
python -m pip install -e .
```

</div>

---

Once you have installed this repo and attained your subnet via the instructions in the nested docs (staging, testing, or main) you can run the miner and validator with the following commands.

## Running Scraping Script (Twitter)
A miner scraps data from Twitter at regular intervals of every 15 seconds and subsequently store this information into their local database. You need Twitter developer account. If you didn't have one, you can bring it from [Twitter Developer Portal](https://developer.twitter.com/en/portal/products).
Then the scraped data is saved to `neurons/twitter_data.db` sothat miner can response to validator's query using this database.
```bash
# To run the scraping script
python neurons/twitterScrap.py 
```
## Define Protocol
You can customize protocol between validator and miner by changing `scraping/protocol.py`.
There're already two protocol classes which are inhereited from bittensor.Synapse class.

```python
class TwitterScrap( bt.Synapse ):

    # Required request input, filled by sending dendrite caller.
    scrap_input: int

    # Optional request output, filled by recieving axon.
    scrap_output: typing.Optional[list[dict]] = None
    
    # scrap_input_hash: str = None
    def deserialize(self) -> list[dict]:
        return self.scrap_output


class CheckMiner( bt.Synapse ):

    # Required request input, send url_hash for check
    check_url_hash: str

    # Return response with tweet searched by url_hash
    check_output: typing.Optional[dict] = None

    def deserialize(self) -> dict:
        return self.check_output
```


## Running Miner
A miner periodically extracts specified data from Twitter using scraping tools or APIs, store this data securely, and then retrieve and provide this data in response to queries from validators, who evaluate the data based on predetermined criteria.
Then also miners response to validator by finding post from url_hash for evaluating their's performance.
```bash
# To run the miner
python -m neurons/miner.py 
    --netuid <your netuid>  # The subnet id you want to connect to
    --subtensor.chain_endpoint <your chain url>  # blockchain endpoint you want to connect
    --wallet.name <your miner wallet> # name of your wallet
    --wallet.hotkey <your validator hotkey> # hotkey name of your wallet
    --logging.debug # Run in debug mode, alternatively --logging.trace for trace mode
```

## Running Validator

The validator issues queries to miners for data, compute scores for the provided data based on uniqueness, rarity, or volume, transfer this scored data to a communal distributed storage system, and adjust weights according to the normalized scores of the miners.

```bash
# To run the validator
python -m neurons/validator.py 
    --netuid <your netuid> # The subnet id you want to connect to
    --subtensor.chain_endpoint <your chain url> # blockchain endpoint you want to connect
    --wallet.name <your validator wallet>  # name of your wallet
    --wallet.hotkey <your validator hotkey> # hotkey name of your wallet
    --wandb.project <your wandb project name> # the wandb project name you want to save to (Default: zhjgapym)
    --wandb.runid <your wandb run id> # the wandb project name you want to save to (Default: scraping_subnet-neurons) 
    --logging.debug # Run in debug mode, alternatively --logging.trace for trace mode
```

</div>

</div>

---

## License
This repository is licensed under the MIT License.
```text
# The MIT License (MIT)
# Copyright © 2023 Yuma Rao

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
```
