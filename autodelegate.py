#!/usr/bin/python3

from __future__ import absolute_import, print_function

import argparse
from subprocess import PIPE, Popen

from logic import epoch_logic

from config import REMAINING_BLOCKS_FOR_AUTO_DELEGATE


def usage():
    return """python autodelegate.py"""


def main(main_args):
    remaining_blocks = epoch_logic.get_remaining_blocks_for_current_epoch()
    print("Remaining blocks: {}".format(remaining_blocks))
    if remaining_blocks < REMAINING_BLOCKS_FOR_AUTO_DELEGATE:
        process = Popen(["autodelegate"], stdout=PIPE)
        process.communicate()


def get_command_line_options():
    parser = argparse.ArgumentParser(description="Autodelegate wrapper. \n\n" + usage())
    return parser.parse_args()


if __name__ == '__main__':
    main_args = get_command_line_options()
    main(main_args)
