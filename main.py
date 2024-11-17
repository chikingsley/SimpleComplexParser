import logging
from pathlib import Path
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from bot.archive_router import DealRouter
from bot.main_simple import SimpleDealBot
from bot.main_complex import ComplexDealBot
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

class MainBot:
    def __init__(self):
        self.simple_bot = SimpleDealBot()
        self.complex_bot = ComplexDealBot()
        self.router = DealRouter()

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Central message handler that routes to appropriate bot"""
        try:
            # Route the message
            flow_type, text = await self.router.route_message(update, context)
            
            if update.callback_query:
                if flow_type == 'simple':
                    await self.simple_bot.handle_callback(update, context)
                else:
                    await self.complex_bot.handle_callback(update, context)
                return
            
            if flow_type == 'simple':
                await self.simple_bot.handle_message(update, context)
            elif flow_type == 'complex':
                await self.complex_bot.handle_message(update, context)
            else:
                await update.message.reply_text(
                    "❌ Invalid message format. Please send either:\n"
                    "1. Formatted deals (TIER1-PARTNER-GEO-...)\n"
                    "2. Detailed deal descriptions"
                )
                
        except Exception as e:
            logger.error(f"Error in message handler: {str(e)}", exc_info=True)
            await update.message.reply_text(
                "❌ An error occurred while processing your message.\n"
                "Please try again or contact support if the issue persists."
            )

    def run(self):
        """Start the bot."""
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            logger.error("No TELEGRAM_BOT_TOKEN found in environment variables")
            return

        # Create application
        application = Application.builder().token(token).build()

        # Add handlers
        application.add_handler(CommandHandler("start", self.simple_bot.start))
        application.add_handler(CommandHandler("help", self.simple_bot.help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Start the bot
        logger.info("Starting bot...")
        application.run_polling()

if __name__ == '__main__':
    bot = MainBot()
    bot.run() 