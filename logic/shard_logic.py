from __future__ import annotations

from collections import defaultdict
from typing import List
from config import NUM_SLOTS
from models import Validator


def get_shard_staking_amounts(
    validators: List[Validator], min_efficient_bid: int, max_efficient_bid: int
) -> Dict[int, int]:
    shard_staking_amounts = defaultdict(int)
    validators.sort(key = lambda v: v.bid, reverse=True)
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
    mean_staking_amount = sum(list(shard_staking_amounts.values())) / len(shard_staking_amounts)
    return {shard: staking_amount / mean_staking_amount for shard, staking_amount in shard_staking_amounts.items()}
