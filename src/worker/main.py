"""Worker Lambda: Processes SQS messages."""

import json
from typing import Any

from aws_lambda_powertools import Logger
from core.dispatcher import Dispatcher
from repositories.telegram_client import TelegramClient
from repositories.user_repository import UserRepository
from services.handlers import register_handlers

logger = Logger()

# --- Initialization (Singleton Pattern) ---
# Initialize these OUTSIDE the handler to reuse connections across warm starts
_bot = TelegramClient()
_user_repo = UserRepository()
_dispatcher = Dispatcher(_bot, _user_repo)

# Register the user's handlers
register_handlers(_dispatcher)
logger.info("Dispatcher initialized and handlers registered")


def lambda_handler(event: dict[str, Any], context: Any) -> None:
    """
    SQS Event Handler.
    """
    logger.info("Received batch", count=len(event.get("Records", [])))

    for record in event["Records"]:
        try:
            # 1. Parse Payload
            update_payload = json.loads(record["body"])

            # 2. Process via Dispatcher
            # The dispatcher handles logic, auto-tracking, and error logging internally
            _dispatcher.process_update(update_payload)

        except Exception as e:
            # Critical: Capture errors to prevent SQS partial batch failure loop
            # In a real prod env, you might want to send this to a DLQ explicitly if needed
            logger.error(
                "Critical error processing record",
                extra={"message_id": record.get("messageId"), "error": e},
                exc_info=True,
            )

    logger.info("Batch processing completed")
