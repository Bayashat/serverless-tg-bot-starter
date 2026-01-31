# Developer Guide

This guide will help you understand how to write your bot logic and extend the template.

## Where to Write Your Code

All your bot logic goes in **`src/worker/handlers.py`**. This is where you'll spend most of your time.

## Using the `@dp.command` Decorator

The template includes a simple dispatcher system. Register command handlers using decorators:

```python
from core.context import Context
from core.dispatcher import Dispatcher

def register_handlers(dp: Dispatcher):
    """Register all your handlers here."""

    @dp.command("start")
    def handle_start(ctx: Context):
        ctx.reply("Welcome! 👋")

    @dp.command("help")
    def handle_help(ctx: Context):
        ctx.reply("Available commands: /start, /help, /ping")

    @dp.command("ping")
    def handle_ping(ctx: Context):
        ctx.reply("🏓 Pong! Serverless is fast.")

    @dp.handle_default
    def handle_echo(ctx: Context):
        """Fallback handler for non-command messages."""
        if ctx.text:
            ctx.reply(f"You said: {ctx.text}")
```

## Understanding the Context Object

The `Context` object (`ctx`) provides easy access to:

- `ctx.text` - Message text
- `ctx.user_id` - Telegram user ID
- `ctx.chat_id` - Chat ID
- `ctx.username` - Username
- `ctx.first_name` - User's first name
- `ctx.reply(text)` - Send a reply message

## Adding New Features

### 1. New Command

Add a `@dp.command("yourcommand")` handler:

```python
@dp.command("weather")
def handle_weather(ctx: Context):
    # Your weather logic here
    ctx.reply("Today's weather: Sunny ☀️")
```

### 2. Database Operations

Use `ctx.user_repo` for DynamoDB operations:

```python
@dp.command("profile")
def handle_profile(ctx: Context):
    user = ctx.user_repo.get_user(ctx.user_id)
    if user:
        ctx.reply(f"Your profile: {user.get('first_name')}")
    else:
        ctx.reply("Profile not found")
```

### 3. External APIs

Import `requests` and make HTTP calls in your handlers:

```python
import requests

@dp.command("quote")
def handle_quote(ctx: Context):
    response = requests.get("https://api.quotable.io/random")
    quote = response.json()
    ctx.reply(f"{quote['content']} — {quote['author']}")
```

## Best Practices

- Keep handlers focused and single-purpose
- Use type hints for better code clarity
- Handle errors gracefully with try-except blocks
- Use the Context object instead of accessing raw update data
- Leverage the user repository for user data management
