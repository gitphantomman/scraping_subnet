
<div align="center">

# **Scraping Subnet v2** <!-- omit in toc -->
[![Discord Chat](https://img.shields.io/discord/308323056592486420.svg)](https://discord.gg/bittensor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 



### The Incentivized Internet <!-- omit in toc -->

[Discord](https://discord.gg/bittensor) • [Network](https://taostats.io/) • [Research](https://bittensor.com/whitepaper)

</div>



This repo contains all the necessary files and functions to define Scraping subnet incentive mechanisms. You can run this project in three ways,
on Bittensor's main-network (real TAO, to be released), Bittensor's test-network (fake TAO), or with your own staging-network. This repo includes instructions for doing all three.

# Introduction

Data scraping is a critical component in numerous AI and machine learning models, often acting as the foundational layer for various subnets, including s1. Our objective is to harvest data from platforms such as Reddit, Twitter, and other social media sites, and aggregate this information into shared storage solutions like `Wasabi` s3 storage. Looking ahead, we intend to leverage the storage subnet of Bittensor to augment our data storage capabilities.

For search and retrieval purposes, validators have access to the indexing table, which is constructed using MongoDB.



- `scraping/protocol.py`: The file where the wire-protocol used by miners and validators is defined.
- `neurons/miner.py`: This script which defines the miner's behavior, i.e., how the miner responds to requests from validators.
- `neurons/validator.py`: This script which defines the validator's behavior, i.e., how the validator requests information from miners and determines scores.




# Installation
This repository requires python3.8 or higher. To install, simply clone this repository and install the requirements.

## Install Bittensor
```bash
$ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/opentensor/bittensor/master/scripts/install.sh)"
```
## Install Dependencies
```bash
git clone https://github.com/gitphantomman/scraping_subnet.git
cd scraping_subnet
python -m pip install -r requirements.txt
python -m pip install -e .
```


# Running Miner
A miner receives a query from the validator approximately every minute.
This query contains specific search keys.
The miner then scrapes data from Twitter or Reddit using Apify and returns the results.

## Prerequisites

For mining you need apify api key. If you don't have one, you can obtain it from the [Apify Settings](https://console.apify.com/account/integrations).
And also you need to set which actor you're going to use and actor ids.
You can get actor ids from [Apify Actors](https://console.apify.com/actors/)

## Configuration with .env


You have to set environment variables in dotenv file. You can use the `.env.example` file as a template.
```bash

# Validator & Miner both MUST!
APIFY_API_KEY=


# Validator Must

WASABI_ENDPOINT_URL='https://s3.us-central-1.wasabisys.com'

# This should be from owner. Please dm to gitphantom
WASABI_ACCESS_KEY_ID=
WASABI_ACCESS_KEY=
INDEXING_API_KEY=

```

The most important env parameter is `APIFY_API_KEY`.


## Running Miner Script

```bash
# To run the miner
cd neurons
python miner.py 
    --netuid 3  # The subnet id you want to connect to
    --subtensor.network finney  # blockchain endpoint you want to connect
    --wallet.name <your miner wallet> # name of your wallet
    --wallet.hotkey <your miner hotkey> # hotkey name of your wallet
    --logging.debug # Run in debug mode, alternatively --logging.trace for trace mode
    --neuron.not_set_weights # Miner cannot set weights. Default is true
    --auto_update # Validators and miners enable auto-update. ("patch" for auto updating)
```

For example:

```bash
python neurons/miner.py --wallet.name test_miner --wallet.hotkey test_miner_1 --subtensor.network finney --netuid 3 --logging.debug --logging.trace --auto_update patch --neurons.not_set_weights False
```

Tips for Optimizing Your Scraper:

    1. Customize your scraper's options by modifying the `run_input` parameter for each scraper.
    2. Keep in mind that faster scraping and more data will result in higher costs for your api_key.
    3. Strive for unique, recent, and accurate data to achieve a higher score.
    4. Avoid submitting fake data as it will result in a score of 0 for that epoch. Validators will randomly choose and check your data against their own scraping scripts and compare the results.

# Running Validator

Validators perform several key tasks in the data mining process. They issue queries to miners, requesting specific data. Once the data is received, validators compute scores based on factors such as uniqueness, rarity, and volume. 

The scoring process involves calculating a time score and a unique score for each piece of data. Validators also verify the authenticity of the data by running their own Apify scripts. This helps to ensure that the data is not fake and contains the correct search key. To accommodate this, you must rent the [epctex/reddit-scraper actor on Apify](https://console.apify.com/actors/jwR5FKaWaGSmkeq2b/console).

Once the data has been scored and verified, it is transferred to a shared storage system on Wasabi S3. Validators then update an indexing table, which is maintained using MongoDB. This table allows validators to efficiently access, search, and fetch data.

Access to the indexing table is secured using an indexing API key, which is provided via an indexing endpoint. This ensures that only authorized validators can access and manipulate the stored data.

## Prerequisites

1. For validating you need apify api key. If you don't have one, you can obtain it from the [Apify Settings](https://console.apify.com/account/integrations).
2. And also you need to set which actor you're going to use and actor ids.
You can get actor ids from [Apify Actors](https://console.apify.com/actors/)
3. You have to get `WASABI_ACCESS_KEY` and `INDEXING_API_KEY` from subnet owner(gitphantom). 

## Configuration with .env


You have to set environment variables in dotenv file. You can use the `.env.example` file as a template.
```bash

# Validator & Miner both MUST!
APIFY_API_KEY=


# Validator Must

WASABI_ENDPOINT_URL='https://s3.us-central-1.wasabisys.com'

# This should be from owner. Please dm to gitphantom
WASABI_ACCESS_KEY_ID=
WASABI_ACCESS_KEY=
INDEXING_API_KEY=

```


## Running Validator Script

```bash
cd neurons
# To run the validator
python validator.py 
    --netuid 3 # The subnet id you want to connect to
    --subtensor.network finney # blockchain endpoint you want to connect
    --wallet.name <your validator wallet>  # name of your wallet
    --wallet.hotkey <your validator hotkey> # hotkey name of your wallet
    --logging.debug # Run in debug mode, alternatively --logging.trace for trace mode
    --auto_update # Validators and miners enable auto-update. ("patch" for auto updating)
```

For example: 
```bash
python neurons/validator.py --wallet.name test_validator --wallet.hotkey test_validator_1 --subtensor.network finney --netuid 3 --auto_update patch --logging.debug --logging.trace
```
---

## License
This repository is licensed under the MIT License.
```text
# The MIT License (MIT)
# Copyright © 2023 Chris Wilson

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


python miner.py --wallet.name test_miner --wallet.hotkey test_miner_1 --subtensor.network test --netuid 18
python validator.py --wallet.name test_validator --wallet.hotkey test_validator_1 --subtensor.network test --netuid 18
