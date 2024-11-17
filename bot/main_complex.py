import logging
from pathlib import Path
import os
from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler as TelegramMessageHandler, 
    CallbackQueryHandler, 
    filters,
    ContextTypes
)
from bot.message import MessageHandler
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ComplexDealBot:
    def __init__(self):
        self.message_handler = MessageHandler()
        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages"""
        await self.message_handler.handle_message(update, context)
        
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries"""
        await self.message_handler.handle_callback(update, context)
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send welcome message when /start is issued"""
        welcome_message = (
            "👋 Welcome to the Deal Parser Bot!\n\n"
            "I can help you submit deals in two formats:\n"
            "1. Formatted deals (TIER1-PARTNER-GEO-...)\n"
            "2. Detailed deal descriptions\n\n"
            "Send me your deals and I'll help you process them!"
        )
        await update.message.reply_text(welcome_message)
        
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send help message when /help is issued"""
        help_text = (
            "📝 I can process deals in two formats:\n\n"
            "1. Formatted deals like:\n"
            "TIER1-Partner-GEO-Language-Source-Model-CPA-CRG-CPL-Funnels-CR-Deduction\n\n"
            "2. Detailed descriptions like:\n"
            "Partner: XYZ Company\n"
            "GEO: UK\n"
            "Price: $1000+10%\n"
            "Source: Facebook"
        )
        await update.message.reply_text(help_text)

def main():
    """Start the bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No TELEGRAM_BOT_TOKEN found in environment variables")
        return

    # Create application
    application = Application.builder().token(token).build()

    # Initialize message handler
    message_handler = MessageHandler()

    # Add handlers
    application.add_handler(
        TelegramMessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            message_handler.handle_message
        )
    )
    
    # Add callback handler - this is what handles button presses
    application.add_handler(
        CallbackQueryHandler(message_handler.handle_callback)
    )

    # Start the bot
    logger.info("Starting bot...")
    application.run_polling()

if __name__ == '__main__':
    main() 