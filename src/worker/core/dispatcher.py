"""
Event Dispatcher.
Handles routing of updates to registered functions using decorators.
"""

from typing import Any, Callable

from aws_lambda_powertools import Logger
from repositories.telegram_client import TelegramClient
from repositories.user_repository import UserRepository

from worker.services.message_formatter import get_translated_text

from .context import Context

logger = Logger()

# Type alias for handler functions
HandlerFunc = Callable[[Context], None]


class Dispatcher:
    """
    Event Dispatcher.
    Handles routing of updates to registered functions using decorators.
    """

    def __init__(self, bot: TelegramClient, user_repo: UserRepository):
        self.bot = bot
        self.user_repo = user_repo

        # Registry for handlers
        self.command_handlers: dict[str, HandlerFunc] = {}
        self.default_handler: HandlerFunc | None = None

    def command(self, command_name: str):
        """
        Decorator to register a command handler.
        Usage:
            @dp.command("start")
            def handle_start(ctx): ...
        """

        def decorator(func: HandlerFunc):
            # Normalize command name (remove / if present)
            clean_name = command_name.lstrip("/")
            self.command_handlers[f"/{clean_name}"] = func
            logger.info(f"Registered command handler: /{clean_name}")
            return func

        return decorator

    def handle_default(self, func: HandlerFunc):
        """Decorator for the fallback handler (catch-all)."""
        self.default_handler = func
        return func

    def process_update(self, update: dict[str, Any]):
        """
        Main entry point to process a single Telegram update.
        """
        ctx = Context(update, self.bot, self.user_repo)

        # --- Middleware: Auto-User Tracking ---
        # Developers don't need to manually save users anymore!
        if ctx.user_id:
            try:
                self.user_repo.register_user(user_id=ctx.user_id, username=ctx.username, first_name=ctx.first_name)
            except Exception as e:
                # Log but don't stop processing
                logger.error(f"Auto-tracking failed: {e}")

        # --- Routing Logic ---
        # 1. Check if it is a command
        text = ctx.text
        if text.startswith("/"):
            # Extract command: "/start@botname" -> "/start"
            command_key = text.split()[0].split("@")[0]

            if command_key in self.command_handlers:
                handler = self.command_handlers[command_key]
                logger.info(f"Dispatching to command handler: {command_key}")
                try:
                    handler(ctx)
                except Exception as e:
                    logger.exception(f"Error in command handler {command_key}: {e}")
                    ctx.reply(get_translated_text("error_occurred", lang_code=ctx.lang_code))
                return

        # 2. If no command matched, or not a command, use Default Handler
        if self.default_handler:
            logger.info("Dispatching to default handler")
            try:
                self.default_handler(ctx)
            except Exception as e:
                logger.exception(f"Error in default handler: {e}")
