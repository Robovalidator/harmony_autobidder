import time
from time import sleep

import client
from logic import epoch_logic, validator_logic, shard_logic

import config
from vstats.alerts import *

VALIDATOR_LENGTHS = []
MAX_VALIDATOR_LENGTHS = 20


def get_validators_and_bid_if_necessary(bidding_enabled=False):
    debug_json = {}
    my_validator = validator_logic.get_my_validator()
    if bidding_enabled:
        # Remove existing keys from the validator not found in the config.
        removed_keys = validator_logic.remove_keys_not_in_config(my_validator)
        if removed_keys:
            # Refresh my_validator
            my_validator = validator_logic.get_my_validator()
            debug_json['keys_not_in_config_removed'] = removed_keys

    validators = validator_logic.get_all_validators_from_snapshot()
    VALIDATOR_LENGTHS.append(len(validators))
    if len(VALIDATOR_LENGTHS) > MAX_VALIDATOR_LENGTHS:
        VALIDATOR_LENGTHS.pop(0)
    avg_validators_length = sum(VALIDATOR_LENGTHS) / (1.0 * len(VALIDATOR_LENGTHS))
    bidding_enabled = len(validators) >= (avg_validators_length - 3) and bidding_enabled
    target_slot = config.TARGET_SLOT

    my_slot_range = validator_logic.get_my_slot_range_for_validators(validators, my_validator)
    num_blocks_left = epoch_logic.get_remaining_blocks_for_current_epoch()
    response_json = dict(
        action=None,
        slots=str(my_slot_range),
        validator=my_validator.to_dict(),
        validators=[v.to_dict() for v in validators],
        num_blocks_left=num_blocks_left,
        num_seconds_left=epoch_logic.get_remaining_seconds_for_current_epoch(),
        interval_seconds=epoch_logic.get_interval_seconds(),
        debug=debug_json
    )
    min_efficient_bid, max_efficient_bid = validator_logic.get_min_max_efficient_bid(validators)
    shard_staking_amounts = shard_logic.get_shard_staking_amounts(validators, min_efficient_bid, max_efficient_bid)

    debug_json['avg_num_validators'] = avg_validators_length
    debug_json['max_efficient_bid'] = max_efficient_bid
    debug_json['min_efficient_bid'] = min_efficient_bid
    debug_json['shard_staking_amounts'] = shard_staking_amounts

    # Check if Final Target Slot is enabled and set target_slot and custom output message
    if bidding_enabled and config.TARGET_SLOT_FINAL_ENABLED_BLOCKS_LEFT > 0 and num_blocks_left <= config.TARGET_SLOT_FINAL_ENABLED_BLOCKS_LEFT:
        target_slot = config.TARGET_SLOT_FINAL
        response_json["TARGET_SLOT_FINAL_ACTIVE"] = u"Target Slot Final: {}, ACTIVE\n" . format(config.TARGET_SLOT_FINAL)
    elif bidding_enabled and config.TARGET_SLOT_FINAL_ENABLED_BLOCKS_LEFT > 0 and num_blocks_left > config.TARGET_SLOT_FINAL_ENABLED_BLOCKS_LEFT :
        response_json["TARGET_SLOT_FINAL_ACTIVE"] = u"Target Slot Final: " + format(config.TARGET_SLOT_FINAL) + ", {} blocks until Active\n" . format((num_blocks_left - config.TARGET_SLOT_FINAL_ENABLED_BLOCKS_LEFT))
    else:
        response_json["TARGET_SLOT_FINAL_ACTIVE"] = ""
       
       
    if not bidding_enabled:
        response_json['interval_seconds'] = 0.5

    changed_keys = False

    validator_lower_bid, key_to_add = validator_logic.get_validator_add_key(my_validator)
    if validator_lower_bid:
        validators_lowering_bid = [validator_lower_bid if v.address == config.VALIDATOR_ADDR else v for v in validators]
        next_slot_range = validator_logic.get_my_slot_range_for_validators(validators_lowering_bid, my_validator)
        response_json["slots_after_lowering_bid"] = str(next_slot_range)

        force_remove_due_to_inefficient = False
        if (
                my_validator.bid > max_efficient_bid
                and next_slot_range.end <= config.NUM_SLOTS
                and config.PREVENT_INEFFICIENT_BID
        ):
            debug_json['force_remove_due_to_inefficient'] = force_remove_due_to_inefficient = True

        if (
                ((my_slot_range.end <= target_slot and next_slot_range.end < target_slot)
                 or force_remove_due_to_inefficient)
                and bidding_enabled
        ):
            response_json["action"] = u"Lowering the bid by adding key {}".format(key_to_add)
            response = client.add_bls_key(key_to_add)
            if response is not None:
                changed_keys = True
                response_json["added_bls_key"] = key_to_add
            else:
                response_json['interval_seconds'] = 1
            validators = validator_logic.get_all_validators()
            my_slot_range = validator_logic.get_my_slot_range_for_validators(validators, my_validator)
            response_json["new_slots"] = str(my_slot_range)

    validator_increase_bid, key_to_remove = validator_logic.get_validator_remove_key(my_validator)
    if validator_increase_bid:
        validators_increasing_bid = [validator_increase_bid if v.address == config.VALIDATOR_ADDR else v
                                     for v in validators]
        next_slot_range = validator_logic.get_my_slot_range_for_validators(validators_increasing_bid,
                                                                           my_validator)
        response_json["slots_after_increasing_bid"] = str(next_slot_range)
        if (
            my_slot_range.end >= target_slot and bidding_enabled and not response_json.get("action")
        ):
            # Max efficient bid calculation must be re-done with a scenario where we remove a key
            _, max_efficient_bid_after_increase = validator_logic.get_min_max_efficient_bid(validators_increasing_bid)
            prevent_bid_due_to_inefficient = False
            if (
                    validator_increase_bid.bid > max_efficient_bid_after_increase
                    and config.PREVENT_INEFFICIENT_BID
                    and my_slot_range.end <= config.NUM_SLOTS
            ):
                prevent_bid_due_to_inefficient = True
                debug_json['prevent_bid_due_to_inefficient'] = prevent_bid_due_to_inefficient

            if not prevent_bid_due_to_inefficient:
                response_json["action"] = u"Increasing the bid by removing key {}".format(key_to_remove)
                response = client.remove_bls_key(key_to_remove)
                if response is not None:
                    response_json["removed_bls_key"] = key_to_remove
                    changed_keys = True
                else:
                    response_json['interval_seconds'] = 1
                
                # VSTATS - CODE START
                # if(my_slot_range.end > NUM_SLOTS):
                # if(my_slot_range.end > target_slot): 
                vstats_slot_alerts(target_slot,my_slot_range,key_to_remove,num_blocks_left)
                # VSTATS - CODE END
                
                validators = validator_logic.get_all_validators()
                my_slot_range = validator_logic.get_my_slot_range_for_validators(validators, my_validator)
                response_json["new_slots"] = str(my_slot_range)

    if changed_keys:
        response_json['interval_seconds'] = 1
    return response_json


def should_show_response_json(prev_response_json, response_json):
    if not response_json:
        raise RuntimeError("response_json should be populated: {}".format(response_json))
    return (not prev_response_json or prev_response_json["slots"] != response_json["slots"]
            or response_json.get("action") or response_json.get("new_slots")
            or prev_response_json["interval_seconds"] != response_json["interval_seconds"])
