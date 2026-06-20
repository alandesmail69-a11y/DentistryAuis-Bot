from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        f"Hi <b>{user.first_name}</b>! 👋\n\n"
        "I'm your Telegram bot. Use /help to see what I can do."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "<b>Available commands:</b>\n\n"
        "/start — Start the bot\n"
        "/help — Show this help message\n"
        "/echo &lt;text&gt; — Repeat your message back\n"
        "/about — About this bot\n"
    )
    await update.message.reply_html(help_text)


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "This bot was built with python-telegram-bot v20+.\n"
        "It uses async handlers and the Application builder pattern."
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        text = " ".join(context.args)
        await update.message.reply_text(text)
    else:
        await update.message.reply_text("Usage: /echo <your message>")
