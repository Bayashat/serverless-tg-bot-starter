"""SQS message client."""

import json
from typing import Any

import boto3
from aws_lambda_powertools import Logger
from repositories import QUEUE_URL

logger = Logger()

# Initialize SQS client globally to reuse TCP connections across Lambda invocations
_SQS_CLIENT = boto3.client("sqs")


class SQSClient:
    """Client for sending raw updates to SQS."""

    def __init__(self) -> None:
        """Initialize SQS client."""
        self.queue_url = QUEUE_URL
        self.sqs_client = _SQS_CLIENT

        logger.debug(f"SQS client initialized with queue URL: {self.queue_url}")

    def send_telegram_update(self, update_payload: dict[str, Any]) -> None:
        """
        Push the raw Telegram update to SQS for asynchronous processing.

        Args:
            update_payload: The full JSON body received from Telegram Webhook.

        Raises:
            Exception: Propagates boto3 exceptions to be handled by the caller.
        """
        try:
            # We treat the payload as an opaque JSON object here.
            # No parsing, no logic. Just Move It.
            self.sqs_client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(update_payload),
            )

            # Log only the update_id if possible, or just a success marker to save costs on large logs
            update_id = update_payload.get("update_id", "unknown")
            logger.info(f"Successfully queued update_id: {update_id}")

        except Exception as e:
            logger.error(f"Failed to send update to SQS: {str(e)}", exc_info=True)
            raise e
