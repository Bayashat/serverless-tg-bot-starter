"""
Execution Context for a single Telegram Update.
"""

from typing import Any

from repositories.telegram_client import TelegramClient
from repositories.user_repository import UserRepository


class Context:
    """
    Wraps the Telegram Update object and provides helper methods.
    This is the main object passed to command handlers.
    """

    def __init__(self, update: dict[str, Any], bot: TelegramClient, user_repo: UserRepository):
        self._update = update
        self._bot = bot
        self._user_repo = user_repo

        # Extract common fields for easy access
        self.message = update.get("message", {})
        self.chat_id = self.message.get("chat", {}).get("id")
        self.user_data = self.message.get("from", {})

        # Handle text safely (some messages might be photos/files)
        self.text = self.message.get("text", "").strip()

        # Parse arguments: "/stock AAPL" -> args=["AAPL"]
        self.args = []
        if self.text and self.text.startswith("/"):
            parts = self.text.split()
            if len(parts) > 1:
                self.args = parts[1:]

    @property
    def user_id(self) -> int | None:
        """Return the user's telegram ID."""
        return self.user_data.get("id")

    @property
    def username(self) -> str | None:
        return self.user_data.get("username")

    @property
    def first_name(self) -> str | None:
        return self.user_data.get("first_name")

    @property
    def lang_code(self) -> str:
        """Return user's language code, defaulting to 'en'."""
        return self.user_data.get("language_code", "en")

    @property
    def message_id(self) -> int | None:
        return self.message.get("message_id")

    def reply(self, text: str) -> None:
        """
        Shorthand to reply to the current message.
        Example: ctx.reply("Hello!")
        """
        if self.chat_id:
            self._bot.send_message(self.chat_id, text)
