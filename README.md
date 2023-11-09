# rotki-balancer
Rotki Balancer is a simple Python script for balancing your crypto portfolio according to your own rules.

Here's what it looks like:
[![asciicast](https://asciinema.org/a/7g7uA6LfALlWAVSyjWEDOmKjc.svg)](https://asciinema.org/a/7g7uA6LfALlWAVSyjWEDOmKjc)

I have a simple system for "allocating" funds to different cryptocurrencies. I assign a percentage to each one, which is how much I intend to hold of those cryptos.

I can say that my assets should look like:
* 40% Bitcoin
* 20% Ethereum
* 10% Dogecoin
* 40% Tezos

and from there, be told what trades I need to execute to reach an intended total value.

The idea is that with regular use over time, this tool will help to build a balanced portfolio.

## Features
Features:
* Simulation mode: Want to show off or test Rotki without any actual assets? Simply write your config, then set simulation_mode: true, and Rotki Balancer will use randomised simulated balances (within 20% of your allocation).
* Allocation management - Buy only mode/Buy and sell mode
   * Buy only: Are you a long term holder? Turn on buy-only mode and Rotki Balancer will tell you how to get as close to your allocation as possible without selling anything.
   * Buy-and-sell: Balancer will tell you what to buy and sell to reach a perfectly balanced portfolio.
     * 🚧 In buy-and-sell mode, make sure to enter a desired held value of at least $1 higher than what you have, to make sure the Balancer still tells you buys and sells.
* Calculate the total value of your assets

## Bugs/antifeatures
* ERC20 tokens and NFTs are not supported yet, but I want to implement that "soon".

## Usage
Before using Rotki, ensure you have the "requests" and "pyyaml" Python modules installed (`pip3 install requests pyyaml`)

Then:
* Clone rotki-balancer from GitHub and put it somewhere safe
* Configure rotki-balancer by copying config.yml.dist to config.yml and customising it
* `cd` to the directory you cloned Rotki Balancer into
* Run `python3 balancer.py`

## Roadmap
Planned features:
* 🚧 In progress: Load your balances from Rotki, filtered for just Blockchain assets
* Net worth mode: Calculate trades needed to reach your chosen allocation for your entire net worth in Rotki (as opposed to just your chosen assets). Net worth mode may be buggy if your desired allocation and your assets in Rotki cannot be reconciled to 100%.
* Overall allocation mode: Tell us how much of your portfolio you want in crypto, and we'll adjust your crypto allocation to match.
* (MAYBE) Support for other asset types in Rotki (e.g. Fiat, DeFi, etc)
* Add support for ERC20 + NFT assets

## Disclaimer(s)
This tool should not be relied on for financial advice. Always check what you are doing!

Rotki is not my product, nor my trademark.

## Licence and Credits
Copyright © Benjamin Arntzen & Raptors With Hats.

Made available with ❤️ under the MIT Licence. 

In other words - you may use this software for any purpose you wish, commercial or personal, and take it apart and study it and share it - essentially whatever you want as long as you give credit!
