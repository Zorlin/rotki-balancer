#!/usr/bin/env python
# -*- coding: utf-8 -*-
import yaml
import logging
import requests
import sys
import random

# Load config file from current directory
with open("config.yml", 'r') as stream:
    try:
        config_data = yaml.safe_load(stream)
    except yaml.YAMLError as exception:
        print(exception)

# Set up logging
def setup_logging():
    # Depending on mode, set INFO or DEBUG logging
    if not config_data["debug_mode"]:
        logging.basicConfig(level=logging.INFO, format='%(message)s')
    else:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    # Suppress the logging output of the requests library
    logging.getLogger("requests").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)

# Load asset balances from Rotki
def load_balances_from_rotki():
    logging.info("Loading asset balances from Rotki...")
    try:
        response = requests.get('http://localhost:4242/api/1/balances', headers={'Content-Type': 'application/json;charset=UTF-8'}, json={'async_query': False, 'ignore_cache': False})
        response.raise_for_status()
        balances = response.json()['result']['assets']
        for asset in balances:
            balances[asset]['usd_value'] = float(balances[asset]['usd_value'])
        return balances
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to load assets from Rotki: {e}")
        return {}

# Load prices from Rotki, used purely for simulations
def load_prices_from_rotki(assets):
    prices = {}

    # Convert asset symbols to uppercase for Rotki API request
    uppercase_assets = [asset.upper() for asset in assets]

    try:
        # Request the latest prices for all assets at once
        response = requests.post(
            'http://localhost:4242/api/1/assets/prices/latest', 
            headers={'Content-Type': 'application/json;charset=UTF-8'},
            json={
                "assets": uppercase_assets,
                "ignore_cache": True,
                "target_asset": "USD"
            }
        )
        response.raise_for_status()
        asset_data = response.json()['result']['assets']
        
        for asset, data in asset_data.items():
            # The price data is the first item in the list, so we extract that
            prices[asset.lower()] = float(data[0])
                
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to load prices from Rotki: {e}")

    return prices

# Simulate balances instead
def simulate_balances_from_config():
    # We're pretending, as we don't want the output to look any different.
    logging.info("Loading asset balances from Rotki...")
    
    # Simulate a total USD value between $50,000 and $200,000, rounded to the nearest 100
    total_usd_value = round(random.uniform(50000, 200000))

    # Directly generate deviated percentages based on the original allocation and ensure they sum up to 100%
    original_percentages = [allocation['allocation'] for allocation in config_data["asset_allocations"]]
    max_deviation = 0.20  # 20%
    deviated_percentages = [p + (random.uniform(-p * max_deviation, p * max_deviation)) for p in original_percentages]
    normalization_factor = 100 / sum(deviated_percentages)
    normalized_percentages = [dp * normalization_factor for dp in deviated_percentages]

    # Fetch real asset prices
    asset_names = [allocation['asset'] for allocation in config_data["asset_allocations"]]
    asset_prices = load_prices_from_rotki(asset_names)

    simulated_balances = {}
    for i, allocation in enumerate(config_data["asset_allocations"]):
        asset_name = allocation['asset']
        deviated_usd_value = (normalized_percentages[i] / 100.0) * total_usd_value
        simulated_amount = deviated_usd_value / asset_prices[asset_name]
        simulated_balances[asset_name.upper()] = {
            'amount': str(simulated_amount),
            'usd_value': float(deviated_usd_value)
        }

    return simulated_balances

def main():
    # Setup logging
    setup_logging()

    # Check if the total percentage allocation of each asset in the config file adds up to 100%
    total_allocation = 0
    for allocation in config_data["asset_allocations"]:
        total_allocation += allocation['allocation']
    if total_allocation != 100:
        logging.error("The total percentage allocation of all assets in the config file must add up to 100%.")
        sys.exit()

    if not config_data.get("simulation_mode", False):
        held_asset_balances = load_balances_from_rotki()
    else:
        held_asset_balances = simulate_balances_from_config()

    # Filter out ERC20 and NFT assets
    held_asset_balances = {
        asset_name: asset
        for asset_name, asset in held_asset_balances.items()
        if not isinstance(asset, dict) or
        not asset_name.startswith("_nft_") and not asset_name.startswith("eip155:1/erc20:")
    }

    # Custom rules to convert asset names to their standard format
    custom_rules = {
        'sol': 'SOL-2',
    }

    # Apply the custom rules to the asset allocations
    for i, allocation in enumerate(config_data["asset_allocations"]):
        asset_name = allocation['asset'].upper()
        asset_name_normalized = asset_name.lower()
        if asset_name_normalized in {key.lower(): value for key, value in custom_rules.items()}:
            asset_name = custom_rules[asset_name_normalized]
        config_data["asset_allocations"][i]['asset'] = asset_name

    # Filter out assets we are not interested in
    held_asset_balances = {
        asset_name: asset
        for asset_name, asset in held_asset_balances.items()
        if asset_name in [allocation['asset'] for allocation in config_data["asset_allocations"]]
    }

    # Calculate the total value held in USD of all relevant assets based on held_asset_balances
    current_total_value = 0
    for asset_name, asset in held_asset_balances.items():
        current_total_value += float(asset['usd_value'])

    logging.info("Current total value held: {:.{}f} USD".format(current_total_value, config_data["floating_precision"]))

    # Print the current amounts and allocations
    logging.info("Current asset allocations:")
    for allocation in config_data["asset_allocations"]:
        asset_name = allocation['asset']
        if asset_name in held_asset_balances:
            asset_amount = held_asset_balances[asset_name]['amount']
            asset_usd_value = float(held_asset_balances[asset_name]['usd_value'])
            asset_allocation = round(asset_usd_value / current_total_value * 100, 2)
            logging.info(f"{asset_name}: {float(asset_amount):.{config_data['floating_precision']}f} ({asset_allocation}%) ({asset_usd_value:.{config_data['floating_precision']}f} USD)")
        else:
            logging.info(f"{asset_name}: 0 (0%) (0 USD)")

    # Ask the user if they want to hold a different total value
    while True:
        new_total_value = input("Enter the new total value you want to hold (in USD), or press [ENTER] to use your existing total: ")
        if new_total_value == "":
            new_total_value = current_total_value
            break
        try:
            new_total_value = float(new_total_value)
            break
        except ValueError:
            print("Invalid input. Please enter a valid total value in USD.")

    # Figure out our target values of what assets *should* be allocated as
    target_values = {}
    for target in config_data["asset_allocations"]:
        asset = target['asset']
        allocation = target['allocation'] / 100.0
        target_values[asset] = allocation * new_total_value

    # Calculate the total underallocation in USD across all assets
    total_underallocation = sum([target_values[asset_name] - float(held_asset_balances[asset_name]['usd_value']) for asset_name in target_values if target_values[asset_name] > float(held_asset_balances[asset_name]['usd_value'])])

    # Calculate the available budget
    budget = new_total_value - current_total_value

    # Check if buy-only mode is enabled
    if config_data.get("buy_only_mode"):
        if budget <= 0:
            logging.info("No need to buy any assets right now.")
            sys.exit()
        else:
            for allocation in config_data["asset_allocations"]:
                asset_name = allocation['asset']
                underallocation = target_values[asset_name] - float(held_asset_balances[asset_name]['usd_value'])
                amount_to_buy = (underallocation / total_underallocation) * budget
                if amount_to_buy > 0:
                    logging.info(f"For {asset_name}, you should buy {amount_to_buy:.2f} USD worth.")
                    held_asset_balances[asset_name]['usd_value'] += amount_to_buy  # Simulate the purchase
            # Calculate the new total value post-purchase
            new_total_value_post_purchase = sum([float(asset['usd_value']) for asset in held_asset_balances.values()])

            logging.info("After purchasing those, your new allocations will be...")

            # Print the projected asset allocations post-purchase
            for allocation in config_data["asset_allocations"]:
                asset_name = allocation['asset']
                asset_usd_value_post_purchase = float(held_asset_balances[asset_name]['usd_value'])
                asset_allocation_post_purchase = round(asset_usd_value_post_purchase / new_total_value_post_purchase * 100, 2)
                logging.info(f"{asset_name}: ({asset_allocation_post_purchase}%) ({asset_usd_value_post_purchase:.2f} USD)")

    else:
        for allocation in config_data["asset_allocations"]:
            asset_name = allocation['asset']
            underallocation = target_values[asset_name] - float(held_asset_balances[asset_name]['usd_value'])
            if underallocation > 0:
                logging.info(f"{asset_name} is underallocated. You should buy {underallocation:.2f} USD worth of it.")
            elif underallocation < 0:
                logging.info(f"{asset_name} is overallocated. You should sell {-underallocation:.2f} USD worth of it.")

if __name__ == "__main__":
    main()
