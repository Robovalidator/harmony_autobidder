from unittest import TestCase
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from logic import bidding_logic
from logic.validator_logic import SlotRange, Validator
import config

class TestBiddingLogic(TestCase):
    def setUp(self):
        # Reset validator lengths before each test
        bidding_logic.VALIDATOR_LENGTHS = []
        
        # Set up test BLS keys that match config
        self.test_bls_keys = ["0x1234567890abcdef", "0xfedcba0987654321"]
        
        # Common test values
        self.test_uptime = 100.0
        self.test_bid = 10000
        self.other_bid = 9000
        self.min_max_bid = (5000, 15000)
        
        # Create mock validator info JSON response
        self.mock_validator_info = {
            "current-epoch-performance": {
                "current-epoch-signing-percent": {
                    "current-epoch-signing-percentage": 98.5
                }
            },
            "validator": {
                "address": config.VALIDATOR_ADDR,
                "name": "Test Validator",
                "bls-public-keys": self.test_bls_keys,
                "min-self-delegation": self.test_bid,
                "max-total-delegation": 100000,
                "rate": "0.1",
                "max-rate": "0.9",
                "max-change-rate": "0.05",
                "update-height": 12345,
                "active": True,
                "commission": {
                    "rate": "0.1",
                    "max-rate": "0.9",
                    "max-change-rate": "0.05"
                }
            }
        }
        
        # Create common validator instances
        self.single_key_validator = Validator(
            address=config.VALIDATOR_ADDR,
            name="Test Validator",
            bid=self.test_bid,
            bls_keys=[self.test_bls_keys[0]],  # Only one key
            num_slots=1,  # Set to low number to encourage key addition
            uptime=self.test_uptime
        )
        
        self.other_validator = Validator(
            address="other_addr",
            name="Other Validator",
            bid=self.other_bid,
            bls_keys=["0xaabbccddee112233"],
            num_slots=8,
            uptime=98.5
        )
        
        self.mock_validator = Validator(
            address=config.VALIDATOR_ADDR,
            name="Test Validator",
            bid=self.test_bid,
            bls_keys=self.test_bls_keys.copy(),
            num_slots=10,
            uptime=self.test_uptime
        )
        
        self.mock_validators = [self.mock_validator, self.other_validator]

    @patch('logic.validator_logic.get_my_validator')
    @patch('logic.validator_logic.get_all_validators_from_snapshot')
    @patch('logic.epoch_logic.get_remaining_blocks_for_current_epoch')
    @patch('logic.epoch_logic.get_remaining_seconds_for_current_epoch')
    @patch('logic.epoch_logic.get_interval_seconds')
    @patch('logic.validator_logic.get_min_max_efficient_bid')
    @patch('logic.validator_logic.get_my_slot_range_for_validators')
    @patch('config.BLS_KEYS', new_callable=list)
    @patch('client.get_json_for_command')
    def test_get_validators_and_bid_if_necessary_bidding_disabled(
        self, mock_get_json, mock_bls_keys, mock_slot_range, mock_min_max_bid, 
        mock_interval, mock_remaining_seconds, mock_remaining_blocks, 
        mock_get_validators, mock_get_my_validator
    ):
        # Setup mocks
        mock_get_json.return_value = self.mock_validator_info
        mock_bls_keys.extend(self.test_bls_keys)
        mock_get_my_validator.return_value = self.mock_validator
        mock_get_validators.return_value = self.mock_validators
        mock_remaining_blocks.return_value = 100
        mock_remaining_seconds.return_value = 1000
        mock_interval.return_value = 10
        mock_min_max_bid.return_value = (5000, 15000)
        mock_slot_range.return_value = SlotRange(start=1, end=5)

        # Call function with bidding disabled
        result = bidding_logic.get_validators_and_bid_if_necessary(bidding_enabled=False)

        # Verify response structure and values
        self.assertIsNone(result['action'])
        self.assertEqual(result['interval_seconds'], 0.5)
        self.assertIn('validators', result)
        self.assertIn('validator', result)
        self.assertEqual(result['num_blocks_left'], 100)
        self.assertEqual(result['num_seconds_left'], 1000)

    @patch('logic.validator_logic.get_my_validator')
    @patch('logic.validator_logic.get_all_validators_from_snapshot')
    @patch('logic.validator_logic.remove_keys_not_in_config')
    @patch('logic.epoch_logic.get_remaining_blocks_for_current_epoch')
    @patch('logic.validator_logic.get_min_max_efficient_bid')
    @patch('logic.validator_logic.get_my_slot_range_for_validators')
    @patch('config.BLS_KEYS', new_callable=list)
    @patch('client.get_json_for_command')
    def test_get_validators_and_bid_if_necessary_with_key_removal(
        self, mock_get_json, mock_bls_keys, mock_slot_range, mock_min_max_bid, 
        mock_remaining_blocks, mock_remove_keys, mock_get_validators, 
        mock_get_my_validator
    ):
        # Setup mocks
        mock_get_json.return_value = self.mock_validator_info
        mock_bls_keys.extend(self.test_bls_keys)
        mock_get_my_validator.return_value = self.mock_validator
        mock_get_validators.return_value = self.mock_validators
        mock_remaining_blocks.return_value = 100
        mock_remove_keys.return_value = ["0x1234567890abcdef"]
        mock_min_max_bid.return_value = (5000, 15000)
        mock_slot_range.return_value = SlotRange(start=1, end=5)

        # Call function with bidding enabled
        result = bidding_logic.get_validators_and_bid_if_necessary(bidding_enabled=True)

        # Verify keys were removed
        self.assertIn('keys_not_in_config_removed', result['debug'])
        mock_remove_keys.assert_called_once()

    def test_should_show_response_json(self):
        # Test case 1: Different slots
        prev_json = {"slots": "1-5", "interval_seconds": 1}
        new_json = {"slots": "2-6", "interval_seconds": 1}
        self.assertTrue(bidding_logic.should_show_response_json(prev_json, new_json))

        # Test case 2: Same data, no action
        prev_json = {"slots": "1-5", "interval_seconds": 1}
        new_json = {"slots": "1-5", "interval_seconds": 1}
        self.assertFalse(bidding_logic.should_show_response_json(prev_json, new_json))

        # Test case 3: Has action
        prev_json = {"slots": "1-5", "interval_seconds": 1}
        new_json = {"slots": "1-5", "action": "some_action", "interval_seconds": 1}
        self.assertTrue(bidding_logic.should_show_response_json(prev_json, new_json))

        # Test case 4: Different interval
        prev_json = {"slots": "1-5", "interval_seconds": 1}
        new_json = {"slots": "1-5", "interval_seconds": 2}
        self.assertTrue(bidding_logic.should_show_response_json(prev_json, new_json))

        # Test case 5: Empty previous json
        new_json = {"slots": "1-5", "interval_seconds": 1}
        self.assertTrue(bidding_logic.should_show_response_json(None, new_json))

        # Test case 6: Empty new json should raise error
        with self.assertRaises(RuntimeError):
            bidding_logic.should_show_response_json(prev_json, {})

    @patch('logic.bidding_logic.validator_logic')  # Patch the entire module
    @patch('logic.bidding_logic.epoch_logic')      # Patch the entire module
    @patch('client.get_json_for_command')
    @patch('client.add_bls_key')
    def test_bidding_logic_add_key(
        self,
        mock_add_key,
        mock_get_json,
        mock_epoch_logic,
        mock_validator_logic,
    ):
        # Setup mocks
        mock_get_json.return_value = self.mock_validator_info
        mock_add_key.return_value = {"result": "success"}

        # Set up BLS keys directly in config
        config.BLS_KEYS = self.test_bls_keys.copy()

        # Set up validator logic mocks
        mock_validator_logic.get_my_validator.return_value = self.single_key_validator
        mock_validator_logic.get_all_validators_from_snapshot.return_value = [self.single_key_validator, self.other_validator]
        mock_validator_logic.get_validator_remove_key.return_value = (None, None)
        mock_validator_logic.get_min_max_efficient_bid.return_value = self.min_max_bid
        mock_validator_logic.get_my_slot_range_for_validators.side_effect = [
            SlotRange(start=1, end=2),  # Initial slot range
            SlotRange(start=1, end=2),  # After checking current position
            SlotRange(start=1, end=4)   # After simulating key addition (better)
        ]

        # Set up epoch logic mocks
        mock_epoch_logic.get_remaining_blocks_for_current_epoch.return_value = 0

        lower_bid_validator = Validator(
            address=config.VALIDATOR_ADDR,
            name="Test Validator",
            bid=self.other_bid,
            bls_keys=[self.test_bls_keys[0]],
            num_slots=1,
            uptime=self.test_uptime
        )
        mock_validator_logic.get_validator_add_key.return_value = (lower_bid_validator, "0xaabbccddee112233")

        try:
            # Call function
            result = bidding_logic.get_validators_and_bid_if_necessary(bidding_enabled=True)

            # Verify key addition
            self.assertIn("added_bls_key", result)
            self.assertEqual(result["interval_seconds"], 1)
            mock_add_key.assert_called_once_with("0xaabbccddee112233")
        finally:
            # Reset config.BLS_KEYS to avoid affecting other tests
            config.BLS_KEYS = []