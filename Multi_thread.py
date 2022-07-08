#!/usr/bin/env python3

"""
# README

## This is an example of a Python script running multiple threads

## What do I need to run this?
    This script requires Python 3.6 or later

## Where do I drop in my code?
    Drop in your code in the following functions:
        - run_worker
        - populate_list

## What else are you not telling?
    The following environment variables are supported:
        - MAX_THREADS
        - LOG_LEVEL
        - LOG_FORMAT
"""

# Require Python 3.6 or later
from concurrent.futures import process
from datetime import datetime
import sys
from tqdm import tqdm

if not (sys.version_info.major >= 3 and sys.version_info.minor >= 6):
    print("ERROR: This script requires Python 3.6 or later")
    exit(1)

import concurrent.futures
import logging
import threading
import time

# Get environment variables
MAX_THREADS = 2000
LOG_LEVEL = os.getenv("LOG_LEVEL", logging.INFO)
# Configure logging
LOG_FORMAT = "%(asctime)s: %(levelname)s %(message)s"
logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL, datefmt="%Y-%m%-d %H:%M:%S")


def run_worker(x):
    time.sleep(x)
    # print(
    #    f"slept for {x} seconds",
    #    f"\nActive Threading count: {threading.active_count() - 1}\n",
    # )


def populate_list(x):
    target_list = []
    for y in range(x):
        target_list.append(y)
    return target_list


def main():
    """
    Main loop to spawn the workers
    """
    loop_counter = 0

    target_list = populate_list(2000)
    failed_list = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        for count, target in tqdm(
            enumerate(target_list), desc="Progress", total=len(target_list), ascii=" .!"
        ):
            try:
                executor.submit(run_worker, 0.5)
            except Exception as e:
                # print(e)
                # print(f"\nEnumerate count: {count}")
                # print(f"\nTarget: {target}")
                failed_info = {"count": count, "target": target, "error message": e}
                failed_list.append(failed_info)
            finally:
                loop_counter = loop_counter + 1


    logging.info("All targets processed")
    logging.info("Main function finished")
    print(f"\nNumber of loop entries: {loop_counter}")
    print(f"\nNumber of failed loop entries: {len(failed_list)}")
    return 0


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time() - start_time
    print(f"\nTime elapsed: {end_time}")
