from unittest import TestCase
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import time

from logic import epoch_logic
from logic.epoch_logic import EpochStats  # Import EpochStats class
import config

class TestEpochLogic(TestCase):
    def setUp(self):
        # Common test values
        self.blocks_per_epoch = EpochStats.EpochSize  # Use actual EpochSize
        self.current_block = 100000
        self.epoch_start_block = 98304  # Example start block
        
        # Set up consistent timestamps
        self.current_timestamp = 1000000000  # Fixed timestamp for testing
        self.epoch_start_timestamp = self.current_timestamp - 3600  # 1 hour ago
        self.epoch_end_timestamp = self.epoch_start_timestamp + 7200  # 2 hours after start
        
        # Mock response for get_latest_header
        self.header_info = {
            "result": {
                "number": hex(self.current_block),  # Block number in hex
                "epoch": 3,  # Current epoch as int
                "epochStartBlock": str(self.epoch_start_block),
                "epochLastBlock": str(self.epoch_start_block + self.blocks_per_epoch - 1),
                "timestamp": hex(self.current_timestamp),  # Try hex timestamp
                "epochTime": self.epoch_end_timestamp - self.epoch_start_timestamp,  # Try epoch duration
            }
        }

    @patch('client.get_latest_header')
    def test_get_remaining_blocks_for_current_epoch(self, mock_get_header):
        # Setup
        mock_get_header.return_value = self.header_info
        
        # Test
        remaining_blocks = epoch_logic.get_remaining_blocks_for_current_epoch()
        
        # Verify
        block_number_end = EpochStats.FirstBlock + EpochStats.EpochSize * (3 - EpochStats.FirstEpoch + 1)
        expected_remaining = (block_number_end - self.current_block) + 1
        self.assertEqual(remaining_blocks, expected_remaining)
        mock_get_header.assert_called_once()

    @patch('client.get_latest_header')
    def test_get_remaining_seconds_for_current_epoch(self, mock_get_header):
        # Setup
        self.header_info = {
            "result": {
                "number": hex(self.current_block),
                "epoch": 3,
                "epochStartBlock": str(self.epoch_start_block),
                "epochLastBlock": str(self.epoch_start_block + self.blocks_per_epoch - 1)
            }
        }
        mock_get_header.return_value = self.header_info
        
        # Test
        remaining_seconds = epoch_logic.get_remaining_seconds_for_current_epoch()
        
        # Calculate expected seconds based on remaining blocks
        blocks_remaining = epoch_logic.get_remaining_blocks_for_current_epoch()
        expected_seconds = blocks_remaining * EpochStats.SecondsPerBlock
        
        # Verify
        self.assertEqual(remaining_seconds, expected_seconds)
        print(f"Blocks remaining: {blocks_remaining}")
        print(f"Seconds per block: {EpochStats.SecondsPerBlock}")
        print(f"Expected seconds: {expected_seconds}")
        print(f"Actual seconds: {remaining_seconds}")

    @patch('logic.epoch_logic.get_remaining_blocks_for_current_epoch')
    @patch('logic.epoch_logic.get_remaining_seconds_for_current_epoch')
    def test_get_interval_seconds(
        self,
        mock_remaining_seconds,
        mock_remaining_blocks,
    ):
        test_cases = [
            # (remaining_seconds, expected_interval)
            (30, 5),                    # < 1 minute: 5 seconds
            (90, 10),                   # < 2 minutes: 10 seconds
            (240, 20),                  # < 5 minutes: 20 seconds
            (540, 45),                  # < 10 minutes: 45 seconds
            (2400, 60),                 # < 1 hour: 1 minute
            (6000, 120),                # < 2 hours: 2 minutes
            (72000, 300),               # < 1 day: 5 minutes
            (100000, 600),              # >= 1 day: 10 minutes
        ]
        
        for remaining_secs, expected_interval in test_cases:
            with self.subTest(remaining_seconds=remaining_secs):
                mock_remaining_seconds.return_value = remaining_secs
                
                interval = epoch_logic.get_interval_seconds()
                print(f"Remaining seconds: {remaining_secs}, Expected: {expected_interval}, Got: {interval}")
                self.assertEqual(interval, expected_interval)
