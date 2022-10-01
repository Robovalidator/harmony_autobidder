import config
from models import Validator, SlotRange
from enums import TimeUnit


def get_response_as_html(response_json):
    validator = Validator.from_dict(response_json["validator"])
    hours = round(response_json["num_seconds_left"] / (TimeUnit.Hour * 1.0), 2)
    shard_staking_amounts = response_json['debug'].get('shard_staking_amounts')
    html = u"".join([
        f"<p>Current slots: {response_json['slots']}</p>\n",
        f"<p>Current epoch uptime: {validator.uptime_as_pct}</p>\n",
        f"<p>If we lower the bid by adding key the slots will be: {response_json.get('slots_after_lowering_bid', 'N/A')}</p>\n",
        f"<p>If we increase the bid by removing a key the slots will be: {response_json.get('slots_after_increasing_bid', 'N/A')}</p>\n",
        f"<p>Max efficient bid: {response_json['debug'].get('max_efficient_bid') or 'Unknown'}",
        f"<p>Epoch progress: {response_json['num_blocks_left']} blocks left ({hours} hours)</p>\n",
    ] + [
        f"<p>Shard {shard} staking amount: {round(amount * 100, 4) }% </p>" for shard, amount in sorted(shard_staking_amounts.items())
    ] + [
        u"<table><tr><td>Slot(s)</td><td>Validator Name</td><td>Bid per slot</td><td>Uptime</td></tr>\n"
    ])

    slot = 1
    for validator_json in response_json["validators"]:
        validator = Validator.from_dict(validator_json)
        slot_range = SlotRange(slot, slot + validator.num_slots - 1)
        class_name = 'other-validator'
        if validator.address == config.VALIDATOR_ADDR:
            class_name = 'robo-validator'
        html += u"<tr class='{}'><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>\n".format(
            class_name, str(slot_range), validator.name, validator.bid, validator.uptime_as_pct)
        slot = slot_range.end + 1

    html += u"</table>\n"
    return html


def get_response_as_text(response_json):
    text = ""
    slot = 1
    for validator_json in response_json["validators"]:
        validator = Validator.from_dict(validator_json)
        slot_range = SlotRange(slot, slot + validator.num_slots - 1)
        text += u"{}: {} ({})\n".format(str(slot_range), validator.name, validator.bid)
        slot = slot_range.end + 1

    validator = Validator.from_dict(response_json["validator"])
    hours = round(response_json["num_seconds_left"] / (TimeUnit.Hour * 1.0), 2)
    shard_staking_amounts = response_json['debug'].pop('shard_staking_amounts', {})

    text += u"".join([
        u"Name: {}\n".format(validator.name),
        u"Target Slot: {}\n".format(config.TARGET_SLOT),
        format(response_json['TARGET_SLOT_FINAL_ACTIVE']),
        u"Current Slots: {}\n".format(response_json["slots"]),
        u"Available Keys: {}\n".format(len(config.BLS_KEYS)),
        u"Current Epoch Uptime: {}\n".format(validator.uptime_as_pct),
        u"Current Bid: {}\n".format(validator.bid),
        # u"BLS keys: {}\n".format(u", ".join(validator.bls_keys)),
        u"If we lower the bid by adding key the slots will be: {}\n".format(
            response_json.get("slots_after_lowering_bid", "N/A")),
        u"If we increase the bid by removing a key the slots will be: {}\n".format(
            response_json.get("slots_after_increasing_bid", "N/A")),
        u"Epoch progress: {} blocks left ({} hours)\n".format(response_json["num_blocks_left"], hours),
        u"Polling interval seconds: {}\n".format(response_json["interval_seconds"]),
        u"Debug data: {}\n".format(response_json["debug"])
    ] + [
        f"Shard {shard} staking amount: {round(amount * 100, 4) }% \n"
        for shard, amount in sorted(shard_staking_amounts.items())
    ])

    removed_bls_key = response_json.get("removed_bls_key")
    if removed_bls_key:
        text += u"Increased the bid by removing key {}\n".format(removed_bls_key)

    added_bls_key = response_json.get("added_bls_key")
    if added_bls_key:
        text += u"Decreased the bid by adding key {}\n".format(added_bls_key)

    new_slots = response_json.get("new_slots")
    if new_slots:
        text += u"New slots after taking action: {}\n".format(response_json["new_slots"])

    return text
