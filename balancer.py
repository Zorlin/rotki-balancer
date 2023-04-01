#!/usr/bin/env python
# -*- coding: utf-8 -*-
import yaml
import logging
import requests
import sys

# Load config file from current directory
with open("config.yml", 'r') as stream:
    try:
        config_data = yaml.safe_load(stream)
    except yaml.YAMLError as exception:
        print(exception)

# Set up logging
def setup_logging():
    if not config_data["debug_mode"]:   
        # By default, show all INFO and above messages
        logging.basicConfig(level=logging.INFO, format='%(message)s')
    else:
        # If debug mode is enabled, show all DEBUG and above messages
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')

# Load asset balances from Rotki
def load_balances_from_rotki():
    logging.info("Loading asset balances from Rotki...")
    try:
        response = requests.get('http://localhost:4242/api/1/balances', headers={'Content-Type': 'application/json;charset=UTF-8'}, json={'async_query': False})
        response.raise_for_status()  # Raise an error if the response status code is not ok
        balances = response.json()['result']['assets']
        return balances
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to load assets from Rotki: {e}")
        return {}

# Main program loop itself
def main():
    global args

    # Parse arguments
    #args = parse_args()

    # Setup logging
    setup_logging()

    # Print config file if in debug mode
    logging.debug("[DEBUG] Config file:")
    logging.debug(config_data)

    held_asset_balances = load_balances_from_rotki()

    #logging.debug("[DEBUG] Held asset balances:")
    #logging.debug(held_asset_balances)

    # Filter out ERC20 and NFT assets
    # If the name starts with "_nft_" it's an NFT
    # If the name starts with eip155:1/erc20: it's an ERC20
    held_asset_balances = {
        asset_name: asset
        for asset_name, asset in held_asset_balances.items()
        if not isinstance(asset, dict) or
        not asset_name.startswith("_nft_") and not asset_name.startswith("eip155:1/erc20:")
    }

    # Some assets have a different name than you might expect. Here, we'll convert your asset names to the names Rotki uses
    # Custom rules to convert asset names to their standard format
    custom_rules = {
        'sol': 'SOL-2',
    }

    # Apply the custom rules to the asset allocations. TODO: This is ugly, find a better way to do this.
    for i, allocation in enumerate(config_data["asset_allocations"]):
        asset_name = allocation['asset'].upper()
        asset_name_normalized = asset_name.lower()
        if asset_name_normalized in {key.lower(): value for key, value in custom_rules.items()}:
            asset_name = custom_rules[asset_name_normalized]
        config_data["asset_allocations"][i]['asset'] = asset_name

    # Filter the list of held_asset_balances to only include the assets we're interested in
    held_asset_balances = {
        asset_name: asset
        for asset_name, asset in held_asset_balances.items()
        if asset_name in [allocation['asset'] for allocation in config_data["asset_allocations"]]
    }

    # Calculate the total value held in USD of all relevant assets based on held_asset_balances
    current_total_value = 0
    for asset_name, asset in held_asset_balances.items():
        current_total_value += float(asset['usd_value'])

    print("DEBUGX: " + str(held_asset_balances))
    logging.info("Current total value held: " + str(current_total_value) + " USD")

    # Ask the user if they want to hold a different total value
    while True:
        new_total_value = input("Enter the new total value you want to hold (in USD), or press [ENTER] to use your existing total: ")
        if new_total_value.lower() == "q":
            # User has chosen to quit
            sys.exit()
        elif new_total_value == "":
            # User has chosen to use their existing total value and just rebalance their portfolio.
            new_total_value = current_total_value
            break
        try:
            new_total_value = float(new_total_value)
            break
        except ValueError:
            print("Invalid input. Please enter a valid total value in USD, or enter 'q' to quit.")
    

if __name__ == "__main__":
    main()
