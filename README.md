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

## Disclaimer(s)
This tool should not be relied on for financial advice. Always check what you are doing!

Rotki is not my product, nor my trademark.

## Usage
* Configure rotki-balancer by copying config.yml.dist to config.yml
* `cd` to this directory
* Run `python3 balancer.py`

## Licence and Credits
Copyright © Benjamin Arntzen & Raptors With Hats.
Made available with ❤️ under the MIT Licence.