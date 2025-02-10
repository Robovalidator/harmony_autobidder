import unittest
from unittest.mock import patch, MagicMock
import client


class TestClient(unittest.TestCase):

    @patch('client.get_json_for_command')
    def test_get_latest_header(self, mock_get_json):
        # Setup mock response
        mock_get_json.return_value = {
            'result': {
                'number': '0x1234',
                'epoch': 5,
                'blockNumber': 4660
            }
        }

        # Call function and verify response
        result = client.get_latest_header()
        if result is None:  # Add defensive check
            self.fail("get_latest_header returned None instead of JSON response")
        
        self.assertEqual(result['result']['number'], '0x1234')
        self.assertEqual(result['result']['epoch'], 5)
        self.assertEqual(result['result']['blockNumber'], 4660)

        # Verify the command was called
        mock_get_json.assert_called_once()

    @patch('client.get_json_for_command')
    def test_remove_bls_key(self, mock_get_json):
        # Setup mock response
        mock_get_json.return_value = {'result': 'success'}

        # Call function
        test_key = "test_bls_key"
        result = client.remove_bls_key(test_key)

        # Verify response
        self.assertEqual(result['result'], 'success')

        # Verify command was called
        mock_get_json.assert_called_once()

    @patch('client.get_json_for_command')
    def test_get_latest_header_empty_response(self, mock_get_json):
        # Setup mock response
        mock_get_json.return_value = None

        # Call function and verify empty response
        result = client.get_latest_header()
        self.assertIsNone(result)

    @patch('client.get_json_for_command')
    def test_remove_bls_key_failed_request(self, mock_get_json):
        # Setup mock to raise exception
        mock_get_json.side_effect = Exception("Command failed")

        # Call function and verify it raises the exception
        test_key = "test_bls_key"
        with self.assertRaises(Exception):
            client.remove_bls_key(test_key)

        # Verify command was called
        mock_get_json.assert_called_once()
