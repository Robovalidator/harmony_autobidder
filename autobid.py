#!/usr/bin/python3

from __future__ import absolute_import, print_function

import argparse
import pprint
import sys
import traceback
from time import sleep

import config
from logic import bidding_logic, epoch_logic, output_logic, validator_logic


def main(main_args):
    if main_args.html:
        html_file = open(config.BASE_HTML_PATH, "r")
        html = html_file.read()
        html = html % (config.MIN_SLOT, config.MAX_SLOT)
        print(html)

    i = 0
    prev_response_json = None

    if main_args.once:
        run_once(main_args)
    else:
        while 1:
            if main_args.raise_errors:
                prev_response_json = run_once(main_args, prev_response_json=prev_response_json)
            else:
                try:
                    prev_response_json = run_once(main_args, prev_response_json=prev_response_json)
                except Exception:
                    ex_type, ex, ex_tb = sys.exc_info()
                    tb = traceback.format_tb(ex_tb, 100)
                    print(u"Got an error! {}\n Traceback: {}".format(repr(ex),
                                                                     "\n".join(tb)))
            interval = (prev_response_json or {}).get("interval_seconds") or epoch_logic.get_interval_seconds()
            sleep(interval)

            if not main_args.html and not main_args.json:
                print(u".", end=u"")
                sys.stdout.flush()

            i += 1

    if main_args.html:
        print(u"</html></body>")


def run_once(main_args, prev_response_json=None):
    bidding_enabled = not main_args.disable_bidding
    response_json = bidding_logic.get_validators_and_bid_if_necessary(bidding_enabled=bidding_enabled)

    if bidding_logic.should_show_response_json(prev_response_json, response_json):
        if main_args.json:
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(response_json)
        elif main_args.html:
            print(output_logic.get_response_as_html(response_json))
        else:
            print(u"\n")
            print(output_logic.get_response_as_text(response_json))

    return response_json


def usage():
    return """python autobid.py"""


def get_command_line_options():
    parser = argparse.ArgumentParser(description="Autobidding service for harmony validators.\n\n" + usage())
    parser.add_argument(
        '-o', '--once', help='Whether or not to run once', action='store_true', default=False
    )
    parser.add_argument(
        '-l', '--html', help='Whether or not to print html', action='store_true', default=False
    )
    parser.add_argument(
        '-j', '--json', help='Whether or not to output json', action='store_true', default=False
    )
    parser.add_argument(
        '-e', '--raise_errors', help='Whether or not to let errors stop execution', action='store_true', default=False
    )
    parser.add_argument(
        '-d', '--disable_bidding', help="If set then disable bidding, just output information", action='store_true',
        default=False
    )
    return parser.parse_args()


if __name__ == '__main__':
    main_args = get_command_line_options()
    main(main_args)
