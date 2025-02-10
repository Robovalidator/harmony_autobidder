#!/usr/bin/python3

from __future__ import absolute_import, print_function

import argparse
import os
import time
from subprocess import PIPE, Popen
from typing import NoReturn, Optional

from config import REMAINING_BLOCKS_FOR_AUTO_DELEGATE
from logic import epoch_logic


def usage() -> str:
    return """python autodelegate.py"""


def main(main_args: argparse.Namespace) -> None:
    remaining_blocks = epoch_logic.get_remaining_blocks_for_current_epoch()
    if remaining_blocks <= 0:
        return
    
    now_timestamp = time.time()
    timestamp_file_path = f"{os.environ['HOME']}/harmony/.autodelegate_ts"
    script_path = f"{os.environ['HOME']}/harmony/scripts/autodelegate"
    try:
        with open(timestamp_file_path, "r") as timestamp_file:
            timestamp_since_autodelegate = float(timestamp_file.read())
    except FileNotFoundError:
        with open(timestamp_file_path, "w") as timestamp_file:
            timestamp_file.write(str(now_timestamp))
        timestamp_since_autodelegate = now_timestamp

    seconds_since_autodelegate = now_timestamp - float(timestamp_since_autodelegate)
    print(f"Remaining blocks: {remaining_blocks}, seconds since previous autodelegate: {seconds_since_autodelegate}")
    if remaining_blocks < REMAINING_BLOCKS_FOR_AUTO_DELEGATE and seconds_since_autodelegate >= 60 * 60 * 3:
        print(f"Autodelegating: {script_path}")
        process = Popen([script_path], stdout=PIPE)
        outs, errs = process.communicate()
        print(f"Outs: {outs} Errs: {errs}")
        with open(timestamp_file_path, "w") as timestamp_file:
            timestamp_file.write(str(now_timestamp))


def get_command_line_options() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Autodelegate wrapper. \n\n" + usage())
    return parser.parse_args()


if __name__ == '__main__':
    main_args = get_command_line_options()
    main(main_args)
