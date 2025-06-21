import json
from telegram import Update
from telegram.ext import MessageHandler, filters, CallbackContext
import messages
import logging

logger = logging.getLogger(__name__)
logger.info("🔄 Инициализация плагина json_validator")

async def json_validator_handler(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(messages.json_validator['prompt'])

async def validate_json(update: Update, context: CallbackContext) -> None:
    try:
        json.loads(update.message.text)
        await update.message.reply_text(messages.json_validator['valid'])
    except json.JSONDecodeError as e:
        await update.message.reply_text(messages.json_validator['invalid'].format(error=str(e)))

def setup(application):
    application.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(f"^{messages.main_menu['buttons']['json_validator']}$"),
        json_validator_handler
    ))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        validate_json
    ))