from __future__ import annotations

from collections import defaultdict
from typing import List, Dict, DefaultDict
from config import NUM_SLOTS
from models import Validator


def get_shard_staking_amounts(
    validators: List[Validator], min_efficient_bid: int, max_efficient_bid: int
) -> Dict[int, float]:
    shard_staking_amounts: DefaultDict[int, int] = defaultdict(int)
    validators.sort(key=lambda v: v.bid, reverse=True)
    slot = 0
    for validator in validators:
        for bls_key in validator.bls_keys:
            if slot >= NUM_SLOTS:
                break
            shard = int(bls_key, 16) % 4
            effective_bid = max(min_efficient_bid, validator.bid)
            effective_bid = min(max_efficient_bid, effective_bid)
            shard_staking_amounts[shard] += effective_bid
            slot += 1
    total_staking_amount = sum(shard_staking_amounts.values())
    mean_staking_amount = total_staking_amount / max(len(shard_staking_amounts), 1)
    return {shard: staking_amount / mean_staking_amount for shard, staking_amount in shard_staking_amounts.items()}
