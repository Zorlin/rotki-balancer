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
        response = requests.get('http://localhost:4242/api/1/balances', headers={'Content-Type': 'application/json;charset=UTF-8'}, json={'async_query': False, 'ignore_cache': True})
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

    # Check if the total percentage allocation of each asset in the config file adds up to 100%
    total_allocation = 0
    for allocation in config_data["asset_allocations"]:
        total_allocation += allocation['allocation']
    if total_allocation != 100:
        logging.error("The total percentage allocation of all assets in the config file must add up to 100%.")
        sys.exit()

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

    # Debug: Print the held asset balances now that we filtered it
    logging.debug("[DEBUG] Printing held asset balances")
    logging.debug(held_asset_balances)
    logging.info("Current total value held: {:.{}f} USD".format(current_total_value, config_data["floating_precision"]))

    # Print the current amounts and allocations
    logging.info("Current asset allocations:")
    for allocation in config_data["asset_allocations"]:
        asset_name = allocation['asset']
        asset_amount = held_asset_balances[asset_name]['amount']
        asset_usd_value = float(held_asset_balances[asset_name]['usd_value'])
        asset_allocation = round(asset_usd_value / current_total_value * 100, 2)
        logging.info(f"{asset_name}: {float(asset_amount):.{config_data['floating_precision']}f} ({asset_allocation}%) ({asset_usd_value:.{config_data['floating_precision']}f} USD)")

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

    # Figure out our target values of what assets *should* be allocated as
    target_values = {}
    for target in config_data["asset_allocations"]:
        asset = target['asset']
        allocation = target['allocation'] / 100.0
        target_values[asset] = allocation * new_total_value

    # Calculate the difference between the current value in USD and the target_value in USD for each asset
    differences = {}
    for allocation in config_data["asset_allocations"]:
        # Existing assets
        asset_name = allocation['asset']
        asset_amount = held_asset_balances[asset_name]['amount']
        asset_usd_value = float(held_asset_balances[asset_name]['usd_value'])
        # The current allocation percentage of this asset based on the new total value we are targeting
        asset_allocation = round(asset_usd_value / new_total_value * 100, 2)

        # If Bitcoin is at 59.31% and our target percentage is 25%, then we are 34.31% overallocated on Bitcoin
        # If Bitcoin is at 25% and our target percentage is 59.31%, then we are 34.31% underallocated on Bitcoin
        difference_percentage = round(allocation['allocation'] - asset_allocation, 2)
        difference_usd = round(target_values[asset_name] - asset_usd_value, 2)
        if difference_percentage > 0:
            logging.info(f"{asset_name} is underallocated by {difference_percentage}% of total asset value (Underallocated by {difference_usd} USD)")
        elif difference_percentage < 0:
            logging.info(f"{asset_name} is overallocated by {abs(difference_percentage)}% of total asset value (Overallocated by {- difference_usd} USD)")
 
    logging.info("Let's work out a strategy:")

    if config_data["experimental"]["selling_is_okay"]:
        # It's okay to sell assets, so let's make everything perfectly even.
        for allocation in config_data["asset_allocations"]:
            # Existing assets
            asset_name = allocation['asset']
            asset_amount = held_asset_balances[asset_name]['amount']
            asset_usd_value = float(held_asset_balances[asset_name]['usd_value'])
            # The current allocation percentage of this asset based on the new total value we are targeting
            asset_allocation = round(asset_usd_value / new_total_value * 100, 2)

            # If Bitcoin is at 59.31% and our target percentage is 25%, then we are 34.31% overallocated on Bitcoin
            # If Bitcoin is at 25% and our target percentage is 59.31%, then we are 34.31% underallocated on Bitcoin
            difference_percentage = round(allocation['allocation'] - asset_allocation, 2)
            difference_usd = round(target_values[asset_name] - asset_usd_value, 2)
            if difference_percentage < 0:
                logging.info(f"{asset_name} is overallocated. You should sell { - difference_usd} USD worth of it.")
            elif difference_percentage > 0:
                logging.info(f"{asset_name} is underallocated. You should buy { difference_usd} USD worth of it.")

    else:
        # We can't sell assets. Let's work out how much we can spend:
        # 1. Calculate the total amount of USD we can spend on buying assets
        total_budget = new_total_value - current_total_value
        if total_budget < 0:
            logging.info("You can't spend any money right now, because you have more assets than you want to hold.")
            sys.exit()
        elif total_budget == 0:
            logging.info("You can't spend any money right now, because you already have as much total value as you want to hold.")
            sys.exit()
        else:
            logging.info(f"You can spend {total_budget} USD on buying assets.")
        print("A strategy for correcting allocations without selling is not available yet.")


if __name__ == "__main__":
    main()
