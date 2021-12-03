from __future__ import annotations

import math
from collections import defaultdict
from time import sleep
from typing import Tuple

import client
from enums import ActiveStatus, BootedStatus, EposStatus, OneUnit, Uptime
from models import SlotRange, Validator

import config


def get_uptime(info_json):
    return float((info_json.get('current-epoch-performance') or {})
                 .get('current-epoch-signing-percent', {})
                 .get('current-epoch-signing-percentage', 1.0))


def extract_validator(info_json):
    validator_json = info_json['validator']
    uptime = get_uptime(info_json)
    delegations = validator_json['delegations']
    name = validator_json['name']
    address = validator_json['address']
    bls_keys = validator_json['bls-public-keys']
    slots = len(bls_keys)
    staked_amount = sum([delegation['amount'] for delegation in delegations]) * OneUnit.Wei
    bid = int(round(staked_amount / (len(bls_keys) * 1.0)))
    return Validator(address, name, bid, bls_keys, slots, uptime)


def get_my_validator():
    response = client.get_validator_info(config.VALIDATOR_ADDR)
    info_json = response['result']
    return extract_validator(info_json)


def get_all_validators():
    i = 0
    validators = []
    existing_addresses = set()
    # my validator may be more up to date
    my_validator = get_my_validator()
    while i < config.MAX_VALIDATORS_PAGES:
        response = client.get_all_validators_info_page(i) or {}
        info_jsons = response.get('result') or []
        if not info_jsons:
            break
        for info_json in info_jsons:
            perf = get_uptime(info_json)
            inactive = info_json['active-status'] == ActiveStatus.Inactive.value
            eligible = info_json['epos-status'] == EposStatus.EligibleElected.value
            validator = extract_validator(info_json)
            if (validator.address == my_validator.address
                    or (not inactive or eligible) and perf >= Uptime.RequiredThreshold):
                if validator.address in existing_addresses:
                    continue
                validators.append(validator)
                existing_addresses.add(validator.address)
        i += 1

    if my_validator:
        validators = [my_validator if val.address == my_validator.address else val for val in validators]
    validators.sort(key = lambda v: v.bid, reverse=True)

    # Prune validators outside of range
    num_slots = 0
    pruned_validators = []
    for validator in validators:
        pruned_validators.append(validator)
        num_slots += len(validator.bls_keys)
        if num_slots >= config.NUM_SLOTS_TO_SHOW:
            break
    return pruned_validators


def get_min_max_efficient_bid(validators: List[Validator]) -> Tuple[int, int]:
    median_slot = config.NUM_SLOTS / 2
    median_slot_upper = median_slot + 1
    median_bid = 0
    median_bid_upper = 0
    slot = 1
    for validator in validators:
        slot_range = SlotRange(slot, slot + validator.num_slots - 1)
        if slot_range.start <= median_slot <= slot_range.end:
            median_bid = validator.bid
        if slot_range.start <= median_slot_upper <= slot_range.end:
            median_bid_upper = validator.bid
        if median_bid and median_bid_upper:
            break
        slot = slot_range.end + 1
    true_median_bid = (median_bid + median_bid_upper) / 2.0
    return true_median_bid * config.EPOS_LOWER_BOUND, true_median_bid * config.EPOS_UPPER_BOUND


def get_my_slot_range_for_validators(validators, my_validator):
    validators.sort(key=lambda v: v.bid, reverse=True)
    slot = 1
    my_slot_range = None

    for validator in validators:
        slot_range = SlotRange(slot, slot + validator.num_slots - 1)

        if validator.address == config.VALIDATOR_ADDR:
            my_slot_range = slot_range
            my_validator = validator

        slot = slot_range.end + 1

    if not my_slot_range:
        my_slot_range = SlotRange(slot, slot + (my_validator.num_slots - 1))

    return my_slot_range


def remove_keys_not_in_config(validator):
    keys = get_keys_not_in_config(validator)
    for key in keys:
        print(f"Removing BLS key {key} since it was not found in the config.")
        client.remove_bls_key(key)
    return keys


def get_keys_not_in_config(validator):
    """Return keys assigned to the validator that aren't in the configuration."""
    return [key for key in validator.bls_keys if key not in config.BLS_KEYS]


def get_missing_key(validator):
    missing_keys = [key for key in config.BLS_KEYS if key not in validator.bls_keys]
    if missing_keys:
        return missing_keys[0]
    return None


def get_validator_add_key(validator):
    missing_key = get_missing_key(validator)
    if not missing_key:
        return None, None
    bls_keys = [missing_key] + validator.bls_keys
    num_slots = len(bls_keys)
    bid = validator.bid * validator.num_slots / (1.0 * num_slots)
    return Validator(validator.address, validator.name, bid, bls_keys, num_slots, validator.uptime), missing_key


def get_validator_remove_key(validator):
    if len(validator.bls_keys) <= 1:
        return None, None
    removed_key = [key for key in config.BLS_KEYS if key in validator.bls_keys][-1]
    bls_keys = [key for key in validator.bls_keys if key != removed_key]
    num_slots = len(bls_keys)
    bid = validator.bid * validator.num_slots / (1.0 * num_slots)
    return Validator(validator.address, validator.name, bid, bls_keys, num_slots, validator.uptime), removed_key
