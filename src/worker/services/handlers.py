"""
User Logic Handlers.
This is where developers add their custom business logic.
"""

from core.context import Context
from core.dispatcher import Dispatcher
from services.message_formatter import get_translated_text


def register_handlers(dp: Dispatcher):
    """
    Register all your handlers here.
    """

    @dp.command("start")
    def handle_start(ctx: Context):
        # Using our multi-language helper
        msg = get_translated_text("start_message", lang_code=ctx.lang_code)
        ctx.reply(msg)

    @dp.command("help")
    def handle_help(ctx: Context):
        msg = get_translated_text("help_message", lang_code=ctx.lang_code)
        ctx.reply(msg)

    # Example of a custom command logic
    @dp.command("ping")
    def handle_ping(ctx: Context):
        ctx.reply("🏓 Pong! Serverless is fast.")

    @dp.handle_default
    def handle_echo(ctx: Context):
        """Echo back whatever the user says (for demo purposes)."""
        if not ctx.text:
            ctx.reply("I can only handle text messages for now.")
            return

        # Demo: simple echo
        ctx.reply(f"You said: {ctx.text}")
