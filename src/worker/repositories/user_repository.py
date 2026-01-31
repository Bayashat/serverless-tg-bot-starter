"""
Repository for Telegram user data access operations.
This is the ONLY layer that should interact with DynamoDB directly for user data.
"""

import time
from typing import Any

import boto3
from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError
from repositories import TG_USERS_TABLE_NAME

logger = Logger()

dynamodb = boto3.resource("dynamodb")


class UserRepository:
    """
    Repository for accessing Telegram user data from DynamoDB.
    Handles all DynamoDB operations for user registration and updates.
    """

    def __init__(self):
        """Initialize DynamoDB resource and table."""
        self._users_table = dynamodb.Table(TG_USERS_TABLE_NAME)
        logger.info("UserRepository initialized", extra={"table_name": TG_USERS_TABLE_NAME})

    def register_user(self, user_id: int, username: str | None = None, first_name: str | None = None) -> None:
        """
        Register or update a Telegram user in DynamoDB with 24-hour debounce.

        This method implements a cost-saving debounce mechanism:
        - Step 1: Read user data (eventually consistent read to save costs)
        - Step 2: Check if user was updated within last 24 hours
        - Step 3: Only write if user doesn't exist or hasn't been updated in 24 hours

        Args:
            user_id: Telegram user ID (integer)
            username: Telegram username (optional, can be None)
            first_name: User's first name (optional, can be None)

        Raises:
            ClientError: If DynamoDB operation fails
            ValueError: If user_id is invalid
        """
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError(f"Invalid user_id: {user_id}. Must be a positive integer.")

        try:
            # Step 1: Read user data
            response = self._users_table.get_item(
                Key={"user_id": user_id},
                ConsistentRead=False,  # Use eventually consistent read to save costs
            )

            item = response.get("Item")
            current_timestamp = int(time.time())  # Current Unix timestamp

            # Step 2: Debounce check
            # If user exists, check if updated within last 24 hours
            if item is not None and "last_seen" in item:
                last_seen = int(item.get("last_seen"))
                time_diff = current_timestamp - last_seen

                # Check if updated within last 24 hours (86400 seconds) - debounce mechanism
                if time_diff < 86400:
                    logger.info(f"User {user_id} update skipped (debounce: {time_diff}s ago)")
                    return

            # Step 3: Write Update
            # We are here because user is NEW or last update was > 24h ago

            # Prepare dynamic SET expression
            set_parts = [
                "last_seen = :last_seen",
                # Atomic counter increment using modern syntax
                # logic: if interaction_days exists, add 1; else start at 0 and add 1
                "interaction_days = if_not_exists(interaction_days, :zero) + :inc",
            ]
            expression_attribute_values: dict[str, Any] = {
                ":last_seen": current_timestamp,  # Unix timestamp
                ":inc": 1,
                ":zero": 0,
            }

            # Conditionally add username and first_name if provided
            if username is not None:
                set_parts.append("username = :username")
                expression_attribute_values[":username"] = username

            if first_name is not None:
                set_parts.append("first_name = :first_name")
                expression_attribute_values[":first_name"] = first_name

            # Construct the final UpdateExpression string
            update_expression = f"SET {', '.join(set_parts)}"

            logger.debug(f"Registering user {user_id} with UpdateExpression: {update_expression}")

            self._users_table.update_item(
                Key={"user_id": user_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
            )

            logger.info(f"Successfully registered/updated user {user_id} (active days +1)")

        except ClientError as e:
            logger.exception(f"Failed to register user {user_id}: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error while registering user {user_id}: {e}")
            raise
