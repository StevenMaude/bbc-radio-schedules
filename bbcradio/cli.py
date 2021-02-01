#!/usr/bin/env python3
# encoding: utf-8
"""
bbcradio.cli
------------
This module implements a CLI using the unofficial bbcradio API.

Copyright (c) 2021 Steven Maude
Licensed under the MIT License, see LICENSE.
"""
import argparse
import sys

import bbcradio
import requests


def list_stations():
    """Retrieves a list of radio stations and prints them.

    Arguments:
        None.

    Returns:
        None.
    """
    stations = bbcradio.Stations()
    for name, url in stations.urls.items():
        print(f"{name} {url}")


def retrieve_schedule(station_name, date):
    """Retrieves and prints a schedule for a station on a given date.

    Arguments:
        station_name: string, radio station name.
        date: string, date in YYYY-MM-DD format.

    Returns:
        None.
    """
    stations = bbcradio.Stations()
    station = stations.select(station_name)

    schedule = bbcradio.Schedule(station, date)
    try:
        schedule.programmes
    except requests.exceptions.HTTPError:
        print(f"Unable to retrieve schedule for {station_name} on {date}.")
        sys.exit(1)

    print(f"Schedule for {schedule.station.name} on {schedule.date}")
    for programme in schedule.programmes:
        p = programme.info
        print("*")
        print(p["start_date"])
        print(
            "|".join(
                [
                    p["series_name"] or "<No series name found>",
                    p["name"] or "<No programme name found>",
                    p["description"] or "<No programme description found>",
                ]
            )
        )
        print(p["url"])


def main():
    parser = argparse.ArgumentParser(prog="bbcradio_cli")
    subparsers = parser.add_subparsers(
        dest="subparser_name", help="sub-command help"
    )

    subparsers.add_parser("stations", help="list stations")

    schedule_parser = subparsers.add_parser(
        "schedule", help="retrieve a schedule"
    )
    schedule_parser.add_argument(
        "station_name", help="name of a station, e.g. BBC Radio 1", type=str
    )
    schedule_parser.add_argument(
        "date", help="date in YYYY-MM-DD format", type=str
    )

    args = parser.parse_args()

    if args.subparser_name == "stations":
        list_stations()
    elif args.subparser_name == "schedule":
        retrieve_schedule(args.station_name, args.date)


if __name__ == "__main__":
    main()
