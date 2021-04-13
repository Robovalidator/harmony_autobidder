import client
from enums import EpochStats, TimeUnit


def get_remaining_blocks_for_current_epoch():
    header_json = client.get_latest_header()
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
        return 2

    if remaining_seconds < TimeUnit.Minute * 2:
        return 3

    if remaining_seconds < TimeUnit.Minute * 10:
        return 10

    if remaining_seconds < TimeUnit.Hour:
        return 30

    if remaining_seconds < 2 * TimeUnit.Hour:
        return TimeUnit.Minute

    if remaining_seconds < TimeUnit.Day:
        return 5 * TimeUnit.Minute

    return 10 * TimeUnit.Minute
