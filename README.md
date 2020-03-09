# Market Making - Pricing and Skewing Models

## Set up for Mac
1. Install Python 3 and pip3
2. Install Visual Studio Code, Python extension for Visual Studio Code
3. Clone this repo. Go to the repo directory.
4. Run ``` pip3 install -r requirements.txt``` to get all neccessary packages.
5. Run ``` python3 pricing_models.py``` to see the result of all pricing models.
6. Run ``` python3 quote_skew_models.py``` to see the result of all quote skew models.

## Content

### 5 pricing models
1. Spread /2, naive theoretical price.
2. Average of book levels 1-3.
3. Weighted average of book levels L1-3 L1:50% L2:35% L3:15%
4. Average of book levels 1-5.
5. Weighted average of book levels L1-5 L1:37.5% L2:27.5% L3:15% L4:10% L5:5%

### 2 quote skew models
1. Naive (symmetric) quote strategy based on price volatility.
2. Inventory-aware quote strategy. Skews quotes to offload inventory.
