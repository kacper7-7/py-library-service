import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_telegram_message(message: str) -> bool:
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    if not token or not chat_id:
        logger.warning("Telegram token or chat_id is not configured in settings.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}

    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        details = e.response.text if e.response is not None else "Brak odpowiedzi"
        logger.error(
            f"Error during send notification to Telegram: {e} | Powód: {details}"
        )
        return False
