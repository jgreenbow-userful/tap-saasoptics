#!/usr/bin/env python3

import argparse
import decimal
import json
import sys

import singer
from singer import metadata, utils

from tap_saasoptics.client import SaaSOpticsClient
from tap_saasoptics.discover import discover
from tap_saasoptics.sync import sync

LOGGER = singer.get_logger()

REQUIRED_CONFIG_KEYS = [
    "token",
    "account_name",
    "server_subdomain",
    "start_date",
    "user_agent",
]


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


def do_discover():

    LOGGER.info("Starting discover")
    catalog = discover()
    json.dump(catalog.to_dict(), sys.stdout, indent=2, cls=DecimalEncoder)
    LOGGER.info("Finished discover")


@singer.utils.handle_top_exception(LOGGER)
def main():

    parsed_args = singer.utils.parse_args(REQUIRED_CONFIG_KEYS)

    with SaaSOpticsClient(
        parsed_args.config["token"],
        parsed_args.config["account_name"],
        parsed_args.config["server_subdomain"],
        parsed_args.config["user_agent"],
    ) as client:

        state = {}
        if parsed_args.state:
            state = parsed_args.state

        if parsed_args.discover:
            do_discover()
        elif parsed_args.catalog:
            sync(
                client=client,
                config=parsed_args.config,
                catalog=parsed_args.catalog,
                state=state,
            )


if __name__ == "__main__":
    main()
