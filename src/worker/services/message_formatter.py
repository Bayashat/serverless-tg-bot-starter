"""
Service for formatting Telegram messages.
"""

from typing import Any

from aws_lambda_powertools import Logger
from services import BOT_DESCRIPTION, BOT_INSTRUCTIONS, BOT_NAME, DEFAULT_LANG

logger = Logger()


TRANSLATIONS = {
    "en": {
        "start_message": (
            "👋 Welcome to {BOT_NAME}!\n\n"
            "I can help you with {BOT_DESCRIPTION}\n"
            "Use the /help command to view available commands."
        ),
        "help_message": (
            "📚 Available commands:\n\n"
            "/start - Start the bot\n"
            "/help - Show help\n\n"
            "💡 How to use:\n"
            "{BOT_INSTRUCTIONS}"
        ),
        "error_occurred": "❌ Unknown command. Use /help to view available commands.",
    },
    "kk": {
        "start_message": (
            "👋 {BOT_NAME} ботқа қош келдіңіз!\n\n"
            "Мен сізге {BOT_DESCRIPTION} бойынша көмектесе аламын.\n"
            "/help командасын қолданып, қолжетімді командаларды көруге болады."
        ),
        "help_message": (
            "📚 Қолжетімді командалар:\n\n"
            "/start - Ботты іске қосу\n"
            "/help - Көмек сұрау\n\n"
            "💡 Қолданылуы:\n"
            "{BOT_INSTRUCTIONS}"
        ),
        "error_occurred": "❌ Белгісіз команда. Қолжетімді командаларды көру үшін /help командасын қолданыңыз.",
    },
    "ru": {
        "start_message": (
            "👋 Добро пожаловать в {BOT_NAME}!\n\n"
            "Я могу помочь вам {BOT_DESCRIPTION}\n"
            "Используйте /help для просмотра доступных команд."
        ),
        "help_message": (
            "📚 Доступные команды:\n\n"
            "/start - Запустить бота\n"
            "/help - Показать справку\n\n"
            "💡 Как использовать:\n"
            "{BOT_INSTRUCTIONS}"
        ),
        "error_occurred": "❌ Неизвестная команда. Используйте /help для просмотра доступных команд.",
    },
}


def get_translated_text(key: str, lang_code: str = "en", **kwargs: Any) -> str:
    """
    Get text translation for a given key and language code.
    Falls back to English if language not supported.
    """
    target_lang = lang_code if lang_code in TRANSLATIONS else DEFAULT_LANG

    text = TRANSLATIONS[target_lang].get(key, key)

    try:
        text = text.format(
            BOT_NAME=BOT_NAME,
            BOT_DESCRIPTION=BOT_DESCRIPTION,
            BOT_INSTRUCTIONS=BOT_INSTRUCTIONS,
            **kwargs,
        )
    except KeyError as e:
        logger.warning(f"Missing format key in translation: {e}")

    return text
