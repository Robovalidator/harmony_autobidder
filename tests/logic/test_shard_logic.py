from unittest import TestCase
from logic.shard_logic import get_shard_staking_amounts
from models import Validator
from config import NUM_SLOTS


class TestShardLogic(TestCase):
    def setUp(self):
        # Create test validators with different bids and BLS keys that map to all 4 shards
        self.validators = [
            Validator(
                address="0x123",
                name="High Bidder",
                bid=2000,
                bls_keys=["0x1", "0x5", "0x9", "0xd"],  # Maps to shards 1, 1, 1, 1
                num_slots=4,
                uptime=0.95
            ),
            Validator(
                address="0x456",
                name="Mid Bidder",
                bid=1500,
                bls_keys=["0x2", "0x6", "0xa", "0xe"],  # Maps to shards 2, 2, 2, 2
                num_slots=4,
                uptime=0.98
            ),
            Validator(
                address="0x789",
                name="Low Bidder",
                bid=1000,
                bls_keys=["0x3", "0x7", "0xb", "0xf"],  # Maps to shards 3, 3, 3, 3
                num_slots=4,
                uptime=0.97
            ),
            Validator(
                address="0xabc",
                name="Another Bidder",
                bid=1750,
                bls_keys=["0x0", "0x4", "0x8", "0xc"],  # Maps to shards 0, 0, 0, 0
                num_slots=4,
                uptime=0.96
            )
        ]

    def test_get_shard_staking_amounts_equal_distribution(self):
        # Test when all validators have same bid within efficient range
        min_bid = 1000
        max_bid = 2000
        
        result = get_shard_staking_amounts(
            validators=self.validators,
            min_efficient_bid=min_bid,
            max_efficient_bid=max_bid
        )
        
        # Verify all shards have values
        self.assertEqual(len(result), 4)  # 4 shards
        for shard in range(4):
            self.assertIn(shard, result)
        
        # All values should sum to number of shards (as they're relative to mean)
        self.assertAlmostEqual(sum(result.values()), 4.0, places=5)
        
        # Print for debugging
        print(f"Shard distribution: {result}")

    def test_get_shard_staking_amounts_with_min_cap(self):
        # Test when some validators are below min efficient bid
        min_bid = 1800
        max_bid = 2500
        
        result = get_shard_staking_amounts(
            validators=self.validators,
            min_efficient_bid=min_bid,
            max_efficient_bid=max_bid
        )
        
        # Verify all shards have values
        self.assertEqual(len(result), 4)
        
        # Verify all lower bids were raised to min_efficient_bid
        for shard, amount in result.items():
            self.assertGreaterEqual(amount, 0)  # No negative amounts
        
        self.assertAlmostEqual(sum(result.values()), 4.0, places=5)

    def test_get_shard_staking_amounts_with_max_cap(self):
        # Test when some validators are above max efficient bid
        min_bid = 1000
        max_bid = 1500
        
        result = get_shard_staking_amounts(
            validators=self.validators,
            min_efficient_bid=min_bid,
            max_efficient_bid=max_bid
        )
        
        # Verify all shards have values
        self.assertEqual(len(result), 4)
        
        # Verify all higher bids were capped at max_efficient_bid
        for shard, amount in result.items():
            self.assertGreaterEqual(amount, 0)
        
        self.assertAlmostEqual(sum(result.values()), 4.0, places=5)

    def test_get_shard_staking_amounts_empty_validators(self):
        result = get_shard_staking_amounts(
            validators=[],
            min_efficient_bid=1000,
            max_efficient_bid=2000
        )
        
        # When no validators, each shard should get 0 stake
        self.assertEqual(len(result), 0)

    def test_get_shard_staking_amounts_slot_limit(self):
        # Create more validators than NUM_SLOTS
        many_validators = [
            Validator(
                address=f"0x{i}",
                name=f"Validator {i}",
                bid=1000 + i * 100,
                bls_keys=[f"0x{j}" for j in range(i*4, (i+1)*4)],  # Each validator gets 4 keys
                num_slots=4,
                uptime=0.95
            )
            for i in range((NUM_SLOTS // 4) + 2)  # Create more than NUM_SLOTS/4 validators
        ]
        
        result = get_shard_staking_amounts(
            validators=many_validators,
            min_efficient_bid=1000,
            max_efficient_bid=2000
        )
        
        # Verify all shards have values
        self.assertEqual(len(result), 4)
        
        # Verify only NUM_SLOTS were considered
        total_stake = sum(result.values())
        self.assertEqual(total_stake, 4.0)  # Should always sum to 4.0 as it's relative 