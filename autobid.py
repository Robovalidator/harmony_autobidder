#!/usr/bin/python3

from __future__ import absolute_import, print_function

import argparse
import sys
import traceback
from time import sleep

import config
from logic import bidding_logic, output_logic


def main(main_args):
    if main_args.html:
        html_file = open(config.BASE_HTML_PATH, "r")
        html = html_file.read()
        html = html % (config.MIN_SLOT, config.MAX_SLOT)
        print(html)

    interval = config.POLL_INTERVAL_SECONDS
    i = 0
    prev_slot_range = None

    if main_args.once:
        run_loop(main_args.html)
    else:
        while 1:
            if main_args.ignore_error:
                try:
                    prev_slot_range = run_loop(main_args.html, prev_slot_range)
                except Exception:
                    ex_type, ex, ex_tb = sys.exc_info()
                    tb = traceback.format_tb(ex_tb, 100)
                    print(u"Got an error! Traceback: {}".format("\n".join(tb)))
            else:
                prev_slot_range = run_loop(main_args.html, prev_slot_range)
            sleep(interval)
            if not main_args.html:
                print(u".", end=u"")
                sys.stdout.flush()
            i += 1

    if main_args.html:
        print(u"</html></body>")


def run_loop(html, prev_slot_range=None):
    response_json = bidding_logic.run_autobid(
        prev_slot_range=prev_slot_range,
        html=main_args.html)
    if prev_slot_range != response_json["slots"]:
        if html:
            print(output_logic.get_response_as_html(response_json))
        else:
            print(u"\n")
            print(output_logic.get_response_as_text(response_json))
    return response_json["slots"]


def usage():
    return """python autobid.py"""


def get_command_line_options():
    parser = argparse.ArgumentParser(description="Autobidding service for harmony validators.\n\n" + usage())
    parser.add_argument(
        '-o', '--once', help='Whether or not to run once', action='store_true', default=False
    )
    parser.add_argument(
        '-r', '--html', help='Whether or not to print html', action='store_true', default=False
    )
    parser.add_argument(
        '-i', '--ignore_error', help='Whether or not to ignore and log errors', action='store_true', default=False
    )

    return parser.parse_args()


if __name__ == '__main__':
    main_args = get_command_line_options()
    main(main_args)
