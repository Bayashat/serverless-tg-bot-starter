"""Telegram Bot API client."""

from typing import Any

import requests
from aws_lambda_powertools import Logger
from repositories import BOT_TOKEN, TELEGRAM_API_BASE

logger = Logger()


class TelegramClient:
    """Client for Telegram Bot API operations."""

    def __init__(self) -> None:
        """Initialize Telegram client."""
        self.bot_token = BOT_TOKEN
        self.api_base = f"{TELEGRAM_API_BASE}{self.bot_token}"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "AWS-Serverless-Telegram-Bot/1.0"})

    def send_message(
        self, chat_id: str, text: str, parse_mode: str = "HTML", reply_markup: dict[str, Any] | None = None
    ) -> None:
        """Send message to Telegram."""
        url = f"{self.api_base}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }

        if reply_markup:
            payload["reply_markup"] = reply_markup

        try:
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(
                "Failed to send message to Telegram",
                extra={"chat_id": chat_id, "error": e},
                extra={"response": e.response.text if e.response else "No response"},
            )
            raise

    def answer_callback_query(self, callback_query_id: str, text: str = None, show_alert: bool = False) -> None:
        """Answer callback query (must be called to dismiss loading state).

        Args:
            callback_query_id: Callback query ID
            text: Text to send
            show_alert: If True, show text as alert instead of notification.
        """
        url = f"{self.api_base}/answerCallbackQuery"

        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text

        if show_alert:
            payload["show_alert"] = show_alert

        try:
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error("Failed to answer callback query", extra={"error": e})
            raise

    def delete_message(self, chat_id: str, message_id: int) -> None:
        """Delete message from Telegram.

        Args:
            chat_id: Telegram chat ID
            message_id: Message ID
        """
        url = f"{self.api_base}/deleteMessage"

        payload = {"chat_id": chat_id, "message_id": message_id}

        try:
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error("Failed to delete message", extra={"message_id": message_id, "error": e})
            raise
