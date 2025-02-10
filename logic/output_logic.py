import config
from models import Validator, SlotRange
from enums import TimeUnit
from typing import Dict, Any, List


def get_response_as_html(response_json: Dict[str, Any]) -> str:
    validator = Validator.from_dict(response_json["validator"])
    hours = round(response_json["num_seconds_left"] / (TimeUnit.Hour * 1.0), 2)
    shard_staking_amounts = response_json['debug'].get('shard_staking_amounts', {})
    html_parts: List[str] = [
        f"<p>Current slots: {response_json['slots']}</p>\n",
        f"<p>Current epoch uptime: {validator.uptime_as_pct}</p>\n",
        f"<p>If we lower the bid by adding key the slots will be: {response_json.get('slots_after_lowering_bid', 'N/A')}</p>\n",
        f"<p>If we increase the bid by removing a key the slots will be: {response_json.get('slots_after_increasing_bid', 'N/A')}</p>\n",
        f"<p>Max efficient bid: {response_json['debug'].get('max_efficient_bid') or 'Unknown'}</p>\n",
        f"<p>Epoch progress: {response_json['num_blocks_left']} blocks left ({hours} hours)</p>\n",
    ]
    
    html_parts.extend([
        f"<p>Shard {shard} staking amount: {round(amount * 100, 4)}% </p>" 
        for shard, amount in sorted(shard_staking_amounts.items())
    ])
    
    html_parts.append(
        "<table><tr><td>Slot(s)</td><td>Validator Name</td><td>Bid per slot</td><td>Uptime</td></tr>\n"
    )

    slot = 1
    for validator_json in response_json["validators"]:
        validator = Validator.from_dict(validator_json)
        slot_range = SlotRange(slot, slot + validator.num_slots - 1)
        class_name = 'robo-validator' if validator.address == config.VALIDATOR_ADDR else 'other-validator'
        html_parts.append(
            f"<tr class='{class_name}'><td>{str(slot_range)}</td><td>{validator.name}</td>"
            f"<td>{validator.bid}</td><td>{validator.uptime_as_pct}</td></tr>\n"
        )
        slot = slot_range.end + 1

    html_parts.append("</table>\n")
    return "".join(html_parts)


def get_response_as_text(response_json: Dict[str, Any]) -> str:
    text_parts: List[str] = []
    slot = 1
    for validator_json in response_json["validators"]:
        validator = Validator.from_dict(validator_json)
        slot_range = SlotRange(slot, slot + validator.num_slots - 1)
        text_parts.append(f"{str(slot_range)}: {validator.name} ({validator.bid})\n")
        slot = slot_range.end + 1

    validator = Validator.from_dict(response_json["validator"])
    hours = round(response_json["num_seconds_left"] / (TimeUnit.Hour * 1.0), 2)
    shard_staking_amounts = response_json['debug'].get('shard_staking_amounts', {})

    text_parts.extend([
        f"Name: {validator.name}\n",
        f"Target slot: {config.TARGET_SLOT}\n",
        f"Current slots: {response_json['slots']}\n",
        f"Available Keys: {len(config.BLS_KEYS)}\n",
        f"Current epoch uptime: {validator.uptime_as_pct}\n",
        f"Current bid: {validator.bid}\n",
        f"If we lower the bid by adding key the slots will be: {response_json.get('slots_after_lowering_bid', 'N/A')}\n",
        f"If we increase the bid by removing a key the slots will be: {response_json.get('slots_after_increasing_bid', 'N/A')}\n",
        f"Epoch progress: {response_json['num_blocks_left']} blocks left ({hours} hours)\n",
        f"Polling interval seconds: {response_json['interval_seconds']}\n",
        f"Debug data: {response_json['debug']}\n"
    ])

    text_parts.extend([
        f"Shard {shard} staking amount: {round(amount * 100, 4)}%\n"
        for shard, amount in sorted(shard_staking_amounts.items())
    ])

    removed_bls_key = response_json.get("removed_bls_key")
    if removed_bls_key:
        text_parts.append(f"Increased the bid by removing key {removed_bls_key}\n")

    added_bls_key = response_json.get("added_bls_key")
    if added_bls_key:
        text_parts.append(f"Decreased the bid by adding key {added_bls_key}\n")

    new_slots = response_json.get("new_slots")
    if new_slots:
        text_parts.append(f"New slots after taking action: {response_json['new_slots']}\n")

    return "".join(text_parts)
