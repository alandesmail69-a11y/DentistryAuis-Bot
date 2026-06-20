# Telegram Bot

A Python Telegram bot built with python-telegram-bot v21 using the async Application pattern.

## Run & Operate

- `cd telegram-bot && python main.py` — run the Telegram bot
- Required env: `TELEGRAM_BOT_TOKEN` — your bot token from [@BotFather](https://t.me/BotFather)

## Stack

- Python 3.11
- python-telegram-bot v21 (async, Application builder pattern)
- python-dotenv for local `.env` support

## Where things live

- `telegram-bot/main.py` — entry point; wires up all handlers and starts polling
- `telegram-bot/bot/config.py` — reads `TELEGRAM_BOT_TOKEN` from env
- `telegram-bot/bot/handlers/commands.py` — `/start`, `/help`, `/about`, `/echo`
- `telegram-bot/bot/handlers/messages.py` — plain text and unknown command handlers
- `telegram-bot/bot/handlers/errors.py` — global error handler

## Architecture decisions

- All handlers are async functions following PTB v20+ conventions.
- Handlers are split by type (commands vs messages vs errors) for clarity.
- Config is centralised in `bot/config.py` — add new env vars there.
- The bot uses long-polling (`run_polling`) which is fine for development; switch to webhooks for production.

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

- Get a bot token from [@BotFather](https://t.me/BotFather) on Telegram (`/newbot`).
- The `TELEGRAM_BOT_TOKEN` secret must be set before starting the workflow.
- Only one instance of the bot can poll at a time — stop existing instances before starting a new one.
