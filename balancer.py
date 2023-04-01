#!/usr/bin/env python
# -*- coding: utf-8 -*-
import yaml
import logging

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

# Load assets from Rotki
def load_assets_from_rotki():
    logging.info("Loading assets from Rotki...")
    

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

    load_assets_from_rotki()



if __name__ == "__main__":
    main()
