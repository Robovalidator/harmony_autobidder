from unittest import TestCase
from unittest.mock import patch, MagicMock

from logic import output_logic
from models import Validator, SlotRange
import config
from enums import TimeUnit


class TestOutputLogic(TestCase):
    def setUp(self):
        self.validator = Validator(
            address="0x123",
            name="Test Validator",
            bid=1000,
            bls_keys=["0xabc", "0xdef"],
            num_slots=2,
            uptime=0.95
        )
        
        self.other_validator = Validator(
            address="0x456",
            name="Other Validator",
            bid=2000,
            bls_keys=["0xghi"],
            num_slots=1,
            uptime=0.98
        )
        
        self.response_json = {
            "validator": self.validator.to_dict(),
            "validators": [
                self.validator.to_dict(),
                self.other_validator.to_dict()
            ],
            "slots": "1-2",
            "num_seconds_left": TimeUnit.Hour * 2,  # 2 hours
            "num_blocks_left": 1000,
            "interval_seconds": 60,
            "slots_after_lowering_bid": "1-3",
            "slots_after_increasing_bid": "1",
            "debug": {
                "max_efficient_bid": 1500,
                "shard_staking_amounts": {
                    "0": 0.25,
                    "1": 0.25,
                    "2": 0.25,
                    "3": 0.25
                }
            }
        }

    def test_get_response_as_html(self):
        # Save original validator address
        original_addr = config.VALIDATOR_ADDR
        config.VALIDATOR_ADDR = "0x123"
        
        try:
            html = output_logic.get_response_as_html(self.response_json)
            
            # Verify key elements are present
            self.assertIn("Current slots: 1-2", html)
            self.assertIn("Current epoch uptime: 95.0%", html)
            self.assertIn("If we lower the bid by adding key the slots will be: 1-3", html)
            self.assertIn("If we increase the bid by removing a key the slots will be: 1", html)
            self.assertIn("Max efficient bid: 1500", html)
            self.assertIn("Epoch progress: 1000 blocks left (2.0 hours)", html)
            
            # Verify shard staking amounts
            self.assertIn("Shard 0 staking amount: 25.0%", html)
            self.assertIn("Shard 1 staking amount: 25.0%", html)
            
            # Verify validator table
            self.assertIn("<table>", html)
            self.assertIn("<tr class='robo-validator'>", html)  # Our validator
            self.assertIn("<tr class='other-validator'>", html)  # Other validator
            self.assertIn("Test Validator", html)
            self.assertIn("Other Validator", html)
            
        finally:
            # Restore original validator address
            config.VALIDATOR_ADDR = original_addr

    def test_get_response_as_text(self):
        text = output_logic.get_response_as_text(self.response_json)
        
        # Verify key elements are present
        self.assertIn("1-2: Test Validator (1000)", text)
        self.assertIn("3: Other Validator (2000)", text)
        self.assertIn("Name: Test Validator", text)
        self.assertIn("Target slot: ", text)  # Value comes from config
        self.assertIn("Current slots: 1-2", text)
        self.assertIn("Available Keys: ", text)  # Value comes from config
        self.assertIn("Current epoch uptime: 95.0%", text)
        self.assertIn("Current bid: 1000", text)
        self.assertIn("If we lower the bid by adding key the slots will be: 1-3", text)
        self.assertIn("If we increase the bid by removing a key the slots will be: 1", text)
        self.assertIn("Epoch progress: 1000 blocks left (2.0 hours)", text)
        self.assertIn("Polling interval seconds: 60", text)
        self.assertIn("Debug data:", text)
        
        # Verify shard staking amounts
        self.assertIn("Shard 0 staking amount: 25.0%", text)
        self.assertIn("Shard 1 staking amount: 25.0%", text)

    def test_get_response_as_text_with_key_changes(self):
        # Add key change information to response
        response_with_changes = self.response_json.copy()
        response_with_changes.update({
            "removed_bls_key": "0xabc",
            "added_bls_key": "0xdef",
            "new_slots": "1-3"
        })
        
        text = output_logic.get_response_as_text(response_with_changes)
        
        # Verify key change messages
        self.assertIn("Increased the bid by removing key 0xabc", text)
        self.assertIn("Decreased the bid by adding key 0xdef", text)
        self.assertIn("New slots after taking action: 1-3", text) 