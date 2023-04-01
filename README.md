# rotki-balancer
Rotki Balancer is a simple Python3 script I am writing to solve a problem of mine.

I have a simple system for "allocating" funds to different cryptos, in terms of percentages I intend to hold of those cryptos.

I would like to be able to say that my assets should look like this:
* 40% Bitcoin
* 20% Ethereum
* 10% Dogecoin
* 40% Tezos

and from there, be told what trades I need to execute to reach an intended total value.

The idea is over time this tool will help to build a balanced portfolio.

## Features
In development:
* 🚧 Load a list of assets from your config file and what allocations you have chosen
* 🚧 Load your balances from Rotki, filtered for just Blockchain assets
* 🚧 Calculate the total value of your assets
* 🚧 Ask for the total value you wish your allocation to be
    * If you are currently unbalanced, it will show you what to do to balance your portfolio. This works even if your total value doesn't change.
    * We may consider adding an option to tell you what to sell, but for now it will simply tell you the best trades to make to even out your allocation.
    * If you are already balanced, it will tell you how much you need to invest to reach your desired allocation.
* 🚧 Calculate the difference between your current allocation and your desired allocation

Planned features:
* Net worth mode: Calculate trades needed to reach your chosen allocation for your entire net worth in Rotki (as opposed to just your chosen assets). Net worth mode may be buggy if your desired allocation and your assets in Rotki cannot be reconciled to 100%.
* Overall allocation mode: Tell us how much of your portfolio you want in crypto, and we'll adjust your crypto allocation to match.
* (MAYBE) Support for other asset types in Rotki (e.g. Fiat, DeFi, etc)

## Bugs/antifeatures
* ERC20 tokens and NFTs are not supported yet, and no support is yet planned. Some day though!

## Disclaimer(s)
This tool should not be relied on for financial advice. Always check what you are doing!

Rotki is not my product, nor my trademark.

## Usage
* Configure rotki-balancer by copying config.yml.dist to config.yml and customising it
* `cd` to this directory
* Run `python3 balancer.py`

## Licence and Credits
Copyright © Benjamin Arntzen & Raptors With Hats.
Made available with ❤️ under the MIT Licence.