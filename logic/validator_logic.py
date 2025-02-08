from __future__ import annotations

from typing import Tuple, List, Dict, Any, Optional, Set

import client
from enums import ActiveStatus, BootedStatus, EposStatus, OneUnit, Uptime
from models import SlotRange, Validator

import config


def get_uptime(info_json: Dict[str, Any]) -> float:
    return float((info_json.get('current-epoch-performance') or {})
                 .get('current-epoch-signing-percent', {})
                 .get('current-epoch-signing-percentage', 1.0))


def extract_validator(info_json: Dict[str, Any]) -> Validator:
    validator_json: Dict[str, Any] = info_json['validator']
    uptime: float = get_uptime(info_json)
    delegations: List[Dict[str, Any]] = validator_json['delegations']
    name: str = validator_json['name']
    address: str = validator_json['address']
    bls_keys: List[str] = validator_json['bls-public-keys']
    slots: int = len(bls_keys)
    staked_amount: int = sum([delegation['amount'] for delegation in delegations]) * OneUnit.Wei
    bid: int = int(round(staked_amount / (len(bls_keys) * 1.0)))
    return Validator(address, name, bid, bls_keys, slots, uptime)


def extract_validator_from_snapshot(info_json: Dict[str, Any]) -> Validator:
    address: str = info_json['validator']
    validator_details = config.VALIDATOR_DETAILS.get(address)
    if validator_details:
        uptime: Optional[float] = validator_details.uptime
        name: str = validator_details.name
    else:
        uptime = None
        name = address
    bls_keys: List[str] = info_json['keys-at-auction']
    slots: int = len(bls_keys)
    bid: int = int(info_json['stake-per-key'] * OneUnit.Wei)
    return Validator(address, name, bid, bls_keys, slots, uptime)


def get_my_validator() -> Optional[Validator]:
    response: Dict[str, Any] = client.get_validator_info(config.VALIDATOR_ADDR)
    info_json: Dict[str, Any] = response['result']
    return extract_validator(info_json)


def get_all_validators_from_snapshot() -> List[Validator]:
    response: Dict[str, Any] = client.get_median_raw_stake_snapshot()
    snapshot: Dict[str, Any] = response['result']

    validators: List[Validator] = []
    # my validator may be more up to date
    my_validator: Optional[Validator] = get_my_validator()
    info_jsons: List[Dict[str, Any]] = snapshot['epos-slot-candidates']
    for info_json in info_jsons:
        validator = extract_validator_from_snapshot(info_json)
        validators.append(validator)

    if my_validator:
        validators = [my_validator if val.address == my_validator.address else val for val in validators]
    validators.sort(key=lambda v: v.bid, reverse=True)

    # Prune validators outside of range
    num_slots: int = 0
    pruned_validators: List[Validator] = []
    for validator in validators:
        pruned_validators.append(validator)
        num_slots += len(validator.bls_keys)
        if num_slots >= config.NUM_SLOTS_TO_SHOW:
            break
    return pruned_validators


def get_all_validators() -> List[Validator]:
    """Slower than get_all_validators_from_snapshot but can be useful to load address to names"""
    i: int = 0
    validators: List[Validator] = []
    existing_addresses: Set[str] = set()
    # my validator may be more up to date
    my_validator: Optional[Validator] = get_my_validator()
    while i < config.MAX_VALIDATORS_PAGES:
        response: Dict[str, Any] = client.get_all_validators_info_page(i) or {}
        info_jsons: List[Dict[str, Any]] = response.get('result') or []
        if not info_jsons:
            break
        for info_json in info_jsons:
            perf: float = get_uptime(info_json)
            inactive: bool = info_json['active-status'] == ActiveStatus.Inactive.value
            eligible: bool = info_json['epos-status'] == EposStatus.EligibleElected.value
            validator: Validator = extract_validator(info_json)
            if (validator.address == my_validator.address
                    or (not inactive or eligible) and perf >= Uptime.RequiredThreshold):
                if validator.address in existing_addresses:
                    continue
                validators.append(validator)
                existing_addresses.add(validator.address)
        i += 1

    if my_validator:
        validators = [my_validator if val.address == my_validator.address else val for val in validators]
    validators.sort(key=lambda v: v.bid, reverse=True)

    # Prune validators outside of range
    num_slots: int = 0
    pruned_validators: List[Validator] = []
    for validator in validators:
        pruned_validators.append(validator)
        num_slots += len(validator.bls_keys)
        if num_slots >= config.NUM_SLOTS_TO_SHOW:
            break
    return pruned_validators


def get_min_max_efficient_bid(validators: List[Validator]) -> Tuple[float, float]:
    median_slot: float = config.NUM_SLOTS / 2
    median_slot_upper: float = median_slot + 1
    median_bid: int = 0
    median_bid_upper: int = 0
    slot: int = 1
    for validator in validators:
        slot_range = SlotRange(slot, slot + validator.num_slots - 1)
        if slot_range.start <= median_slot <= slot_range.end:
            median_bid = validator.bid
        if slot_range.start <= median_slot_upper <= slot_range.end:
            median_bid_upper = validator.bid
        if median_bid and median_bid_upper:
            break
        slot = slot_range.end + 1
    true_median_bid: float = (median_bid + median_bid_upper) / 2.0
    return true_median_bid * config.EPOS_LOWER_BOUND, true_median_bid * config.EPOS_UPPER_BOUND


def get_my_slot_range_for_validators(validators: List[Validator], my_validator: Validator) -> SlotRange:
    validators.sort(key=lambda v: v.bid, reverse=True)
    slot: int = 1
    my_slot_range: Optional[SlotRange] = None

    for validator in validators:
        slot_range = SlotRange(slot, slot + validator.num_slots - 1)

        if validator.address == config.VALIDATOR_ADDR:
            my_slot_range = slot_range
            my_validator = validator

        slot = slot_range.end + 1

    if not my_slot_range:
        my_slot_range = SlotRange(slot, slot + (my_validator.num_slots - 1))

    return my_slot_range


def remove_keys_not_in_config(validator: Validator) -> List[str]:
    keys: List[str] = get_keys_not_in_config(validator)
    for key in keys:
        print(f"Removing BLS key {key} since it was not found in the config.")
        client.remove_bls_key(key)
    return keys


def get_keys_not_in_config(validator: Validator) -> List[str]:
    """Return keys assigned to the validator that aren't in the configuration."""
    return [key for key in validator.bls_keys if key not in config.BLS_KEYS]


def get_missing_key(validator: Validator) -> Optional[str]:
    missing_keys: List[str] = [key for key in config.BLS_KEYS if key not in validator.bls_keys]
    if missing_keys:
        return missing_keys[0]
    return None


def get_validator_add_key(validator: Validator) -> Tuple[Optional[Validator], Optional[str]]:
    missing_key: Optional[str] = get_missing_key(validator)
    if not missing_key:
        return None, None
    bls_keys: List[str] = [missing_key] + validator.bls_keys
    num_slots: int = len(bls_keys)
    bid: float = validator.bid * validator.num_slots / (1.0 * num_slots)
    return Validator(validator.address, validator.name, bid, bls_keys, num_slots, validator.uptime), missing_key


def get_validator_remove_key(validator: Validator) -> Tuple[Optional[Validator], Optional[str]]:
    if len(validator.bls_keys) <= 1:
        return None, None
    removed_key: str = [key for key in config.BLS_KEYS if key in validator.bls_keys][-1]
    bls_keys: List[str] = [key for key in validator.bls_keys if key != removed_key]
    num_slots: int = len(bls_keys)
    bid: float = validator.bid * validator.num_slots / (1.0 * num_slots)
    return Validator(validator.address, validator.name, bid, bls_keys, num_slots, validator.uptime), removed_key
