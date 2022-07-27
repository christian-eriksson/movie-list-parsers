#!/usr/bin/env python
import os
import re
import sys
import csv
from typing import List


def parse_list_into_accumulators(
    path: str, accumulator: List[str], unique_accumulator: dict
):
    with open(path, "rt") as csvfile:
        reader = csv.reader(csvfile, quotechar='"')
        for row in reader:
            id = row[1]
            if id.startswith("tt"):
                imdb_id = f"tt{id}"
                description = row[4]
                season_match = re.match(
                    r".*season (\d+)(-(\d+))?(: ep\. (\d+)(-(\d+))?)?.*",
                    description,
                    flags=re.IGNORECASE,
                )
                seasons = []
                episodes = []
                if season_match:
                    start_season = int(season_match.group(1))
                    end_season = start_season
                    if season_match.group(2):
                        end_season = int(season_match.group(3))
                    seasons = [*range(start_season, end_season + 1)]
                    if season_match.group(4):
                        start_episode = int(season_match.group(5))
                        end_episode = start_episode
                        if season_match.group(6):
                            end_episode = int(season_match.group(7))
                        episodes = [*range(start_episode, end_episode + 1)]

                parsed_row = f"{id};{row[5]};{'|'.join([str(season) for season in seasons])};{'|'.join([str(episode) for episode in episodes])}"
                accumulator.append(parsed_row)
                if not imdb_id in accumulator:
                    unique_accumulator[imdb_id] = parsed_row


def parse_path_into_accumulators(
    path: str, accumulator: List[str], unique_accumulator: dict
):
    if os.path.isdir(path):
        for item in os.scandir(path):
            parse_path_into_accumulators(
                f"{path}/{item.name}", accumulator, unique_accumulator
            )
    elif os.path.isfile(path):
        parse_list_into_accumulators(path, accumulator, unique_accumulator)
    else:
        print(f"ERROR: '{path}' is not a file or directory", file=sys.stderr)
        exit(1)


def parse_path(path: str, with_duplicates=False):
    unique_accumulator = {}
    accumulator = []
    parse_path_into_accumulators(path, accumulator, unique_accumulator)
    if with_duplicates:
        return accumulator
    else:
        return list(unique_accumulator.values())


if __name__ == "__main__":
    if "-d" in sys.argv or "--allow-duplicates" in sys.argv:
        allow_duplicates = True
        try:
            sys.argv.remove("-d")
        except:
            sys.argv.remove("--allow-duplicates")
    else:
        allow_duplicates = False

    try:
        path = sys.argv[1]
    except:
        print("ERROR: provide path to parse in arg 1", file=sys.stderr)
        exit(1)

    parsed_list = parse_path(path, with_duplicates=allow_duplicates)

    for list in parsed_list:
        print(list)
