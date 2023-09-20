
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
The Bittensor blockchain hosts multiple self-contained incentive mechanisms 'subnets'. Subnets are playing fields through which miners (those producing value) and validators (those producing consensus) determine together the proper distribution of TAO for the purpose of incentivizing the creation of value, i.e. generating digital commodities, such as intelligence, or data. Each consists of a wire protocol through which miners and validators interact and their method of interacting with Bittensor's chain consensus engine [Yuma Consensus](https://bittensor.com/documentation/validating/yuma-consensus) which is designed to drive these actors into agreement about who is creating value.


![Alt text](docs/Screenshot_18.png)


Data scraping plays a pivotal role in many AI and machine learning models, often serving as the partial layer for various subnets, including s1. We aim to extract data from platforms like Reddit, Twitter, and other social media sites, consolidating this information into shared storage solutions like Weights & Biases (wandb). In the future, we plan to utilize the storage subnet of Bittensor to enhance our data storage capabilities. 

- `template/protocol.py`: The file where the wire-protocol used by miners and validators is defined.
- `neurons/miner.py`: This script which defines the miner's behavior, i.e., how the miner responds to requests from validators.
- `neurons/validator.py`: This script which defines the validator's behavior, i.e., how the validator requests information from miners and determines scores.

</div>

---

# Running the project
Before running the project you will need to attain a subnetwork on either Bittensor's main network, test network, or your own staging network. To create subnetworks on each of these subnets follow the instructions in files below:
- `docs/running_on_staging.md`
- `docs/running_on_testnet.md`
- `docs/running_on_mainnet.md`

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
```bash
# To run the miner
python -m neurons/miner.py 
    --netuid <your netuid>  # Must be attained by following the instructions in the docs/running_on_*.md files
    --subtensor.chain_endpoint <your chain url>  # Must be attained by following the instructions in the docs/running_on_*.md files
    --wallet.name <your miner wallet> # Must be created using the bittensor-cli
    --wallet.hotkey <your validator hotkey> # Must be created using the bittensor-cli
    --logging.debug # Run in debug mode, alternatively --logging.trace for trace mode

# To run the validator
python -m neurons/validator.py 
    --netuid <your netuid> # Must be attained by following the instructions in the docs/running_on_*.md files
    --subtensor.chain_endpoint <your chain url> # Must be attained by following the instructions in the docs/running_on_*.md files
    --wallet.name <your validator wallet>  # Must be created using the bittensor-cli
    --wallet.hotkey <your validator hotkey> # Must be created using the bittensor-cli
    --wandb.project <your wandb project name> # Default: zhjgapym
    --wandb.runid <your wandb run id> # Default: scraping_subnet-neurons
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
