import client
import config
from logic import validator_logic


def run_autobid(prev_slot_range=None):
    validators = validator_logic.get_all_validators()
    my_slot_range, my_validator = validator_logic.get_my_slot_range_for_validators(validators)
    response_json = dict(
        action=None,
        slots=str(my_slot_range),
        uptime=str(my_validator.uptime_as_pct),
        validator=my_validator.to_dict(),
        validators=[v.to_dict() for v in validators]
    )

    validator_lower_bid, key_to_add = validator_logic.get_validator_add_key(my_validator)
    if validator_lower_bid:
        validators_lowering_bid = [validator_lower_bid if v.address == config.VALIDATOR_ADDR else v for v in validators]
        next_slot_range, next_validator = validator_logic.get_my_slot_range_for_validators(validators_lowering_bid)
        response_json["slots_after_lowering_bid"] = str(next_slot_range)

        if my_slot_range.end <= config.MIN_SLOT and next_slot_range.end <= config.MAX_SLOT:
            response_json["action"] = u"Lowering the bid by adding key {}".format(key_to_add)
            response_json["added_bls_key"] = key_to_add
            client.add_bls_key(key_to_add)
            validators = validator_logic.get_all_validators()
            my_slot_range, my_validator = validator_logic.get_my_slot_range_for_validators(validators)
            response_json["new_slots"] = str(my_slot_range)

    validator_increase_bid, key_to_remove = validator_logic.get_validator_remove_key(my_validator)
    if validator_increase_bid:
        validators_increasing_bid = [validator_increase_bid if v.address == config.VALIDATOR_ADDR else v
                                     for v in validators]
        next_slot_range, next_validator = validator_logic.get_my_slot_range_for_validators(validators_increasing_bid)
        response_json["slots_after_increasing_bid"] = str(next_slot_range)
        if my_slot_range.end >= config.MAX_SLOT:
            response_json["action"] = u"Increasing the bid by removing key {}".format(key_to_remove)
            client.remove_bls_key(key_to_remove)
            response_json["removed_bls_key"] = key_to_remove
            validators = validator_logic.get_all_validators()
            my_slot_range, my_validator = validator_logic.get_my_slot_range_for_validators(validators)
            response_json["new_slots"] = str(my_slot_range)

    return response_json
