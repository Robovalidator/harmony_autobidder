from time import sleep

import client
from enums import EpochStats, TimeUnit


def get_remaining_blocks_for_current_epoch(retries=10):
    if retries == 0:
        # Just return a number so we can continue
        return 10
    header_json = client.get_latest_header()
    if not header_json:
        sleep(1.0)
        print("Warning: Got an empty response from client.get_latest_header()")
        return get_remaining_blocks_for_current_epoch(retries=retries-1)
    result_json = header_json['result']
    if 'number' in result_json:
        # New RPC response
        block_number = int(result_json['number'], 16)
    else:
        block_number = result_json['blockNumber']
    current_epoch = result_json['epoch']
    block_number_end = get_block_number_for_epoch_end(current_epoch)
    return (block_number_end - block_number) + 1


def get_block_number_for_epoch_end(epoch):
    return EpochStats.FirstBlock + EpochStats.EpochSize * (epoch - EpochStats.FirstEpoch + 1)


def get_remaining_seconds_for_current_epoch():
    remaining_blocks = get_remaining_blocks_for_current_epoch()
    return remaining_blocks * EpochStats.SecondsPerBlock


def get_interval_seconds():
    remaining_seconds = get_remaining_seconds_for_current_epoch()
    if remaining_seconds < TimeUnit.Minute:
        return 5

    if remaining_seconds < TimeUnit.Minute * 2:
        return 10

    if remaining_seconds < TimeUnit.Minute * 5:
        return 20

    if remaining_seconds < TimeUnit.Minute * 10:
        return 45

    if remaining_seconds < TimeUnit.Hour:
        return TimeUnit.Minute

    if remaining_seconds < 2 * TimeUnit.Hour:
        return 2 * TimeUnit.Minute

    if remaining_seconds < TimeUnit.Day:
        return 5 * TimeUnit.Minute

    return 10 * TimeUnit.Minute
