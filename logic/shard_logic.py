from __future__ import annotations

from collections import defaultdict
from typing import List

from models import Validator


def get_shard_staking_amounts(validators: List[Validator]) -> Dict[int, int]:
    shard_staking_amounts = defaultdict(int)
    for validator in validators:
        for bls_key in validator.bls_keys:
            shard = int(bls_key, 16) % 4
            shard_staking_amounts[shard] += validator.bid
    mean_staking_amount = sum(list(shard_staking_amounts.values())) / len(shard_staking_amounts)
    return {shard: staking_amount / mean_staking_amount for shard, staking_amount in shard_staking_amounts.items()}
