from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
import requests
from notification.utils import send_telegram_message


class TelegramUtilsTestCase(TestCase):
    @override_settings(TELEGRAM_BOT_TOKEN="fake_token", TELEGRAM_CHAT_ID="fake_id")
    @patch("notification.utils.requests.post")
    def test_send_telegram_message_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = send_telegram_message("Test message")

        self.assertTrue(result)
        mock_post.assert_called_once()

    @override_settings(TELEGRAM_BOT_TOKEN="", TELEGRAM_CHAT_ID="")
    @patch("notification.utils.requests.post")
    def test_send_telegram_message_missing_credentials(self, mock_post):
        result = send_telegram_message("Test message")

        self.assertFalse(result)
        mock_post.assert_not_called()

    @override_settings(TELEGRAM_BOT_TOKEN="fake_token", TELEGRAM_CHAT_ID="fake_id")
    @patch("notification.utils.requests.post")
    def test_send_telegram_message_network_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.RequestException("Network Error")

        result = send_telegram_message("Test message")

        self.assertFalse(result)
