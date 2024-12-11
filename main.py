import logging
from pathlib import Path
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler
from bot.router import DealRouter
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
            
            # Handle callback queries
            if update.callback_query:
                logger.debug(f"Handling callback query: {update.callback_query.data}")
                # Always route callbacks to complex bot for better handling
                await self.complex_bot.handle_callback(update, context)
                return
            
            # Handle text messages
            if flow_type == 'simple':
                await self.simple_bot.handle_message(update, context)
            elif flow_type == 'complex':
                await self.complex_bot.handle_message(update, context)
            else:
                await update.message.reply_text(
                    "❌ Invalid message format. Please send either:\n"
                    "1. Formatted deals (TIER1-PARTNER-GEO-...)\n"
                    "2. Messages starting with 'Partner: '"
                )
                
        except Exception as e:
            logger.error(f"Error in message handler: {str(e)}", exc_info=True)
            # Use effective_message to handle both regular messages and callbacks
            message = update.effective_message
            if message:
                await message.reply_text(
                    "❌ An error occurred while processing your message.\n"
                    "Please try again or contact support if the issue persists."
                )

    def run(self):
        """Start the bot."""
        # Create application and add handlers
        application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

        # Add handlers
        application.add_handler(CommandHandler("start", self.simple_bot.start))
        application.add_handler(CommandHandler("help", self.simple_bot.help_command))
        application.add_handler(CommandHandler("prompt", self.simple_bot.prompt))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Set up conversation handler for the complex bot
        complex_conv_handler = ConversationHandler(
            entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, self.complex_bot.handle_message)],
            states={
                self.complex_bot.EDIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.complex_bot._handle_edit_input)]
            },
            fallbacks=[],
            name="complex_conversation"
        )
        application.add_handler(complex_conv_handler)

        # Add callback query handler at the application level
        application.add_handler(CallbackQueryHandler(self.complex_bot.handle_callback))

        # Start polling
        application.run_polling()

if __name__ == '__main__':
    bot = MainBot()
    bot.run() 