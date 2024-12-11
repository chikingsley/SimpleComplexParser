from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    filters, 
    CallbackContext,
    ContextTypes
)
from main import MainBot
import os
from fastapi import FastAPI, Request, Response
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO if os.getenv('ENVIRONMENT') == 'production' else logging.DEBUG
)
logger = logging.getLogger(__name__)

# Initialize components
app = FastAPI(title="Telegram Bot API")
bot = MainBot()
application = None

@app.on_event("startup")
async def startup_event():
    """Initialize bot application on startup"""
    global application
    try:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
            
        # Build application
        application = Application.builder().token(token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", bot.simple_bot.start))
        application.add_handler(CommandHandler("help", bot.simple_bot.help_command))
        
        # Add callback query handler for button clicks
        application.add_handler(CallbackQueryHandler(bot.handle_message))
        
        # Add message handler for text messages
        application.add_handler(MessageHandler(
            filters.TEXT | filters.COMMAND | filters.StatusUpdate.ALL, 
            bot.handle_message
        ))
        
        # Add error handler
        async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
            logger.error(f"Exception while handling an update: {context.error}")
            if isinstance(update, Update):
                if update.callback_query:
                    await update.callback_query.answer(
                        text="An error occurred while processing your request."
                    )
        
        application.add_error_handler(error_handler)
        
        # Initialize and start the application
        await application.initialize()
        await application.start()
        logger.info("Bot application initialized successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}", exc_info=True)
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global application
    try:
        if application:
            logger.info("Shutting down bot application...")
            await application.stop()
            await application.shutdown()
            logger.info("Bot application shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}", exc_info=True)

@app.post("/api/telegram")
async def telegram_webhook(request: Request):
    """Handle incoming webhook requests from Telegram"""
    try:
        # Log incoming request
        logger.info("Received webhook request")
        
        # Verify webhook secret if configured
        webhook_secret = os.getenv("WEBHOOK_SECRET")
        if webhook_secret:
            secret_header = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
            logger.info(f"Webhook secret check - Expected: {webhook_secret}, Received: {secret_header}")
            if secret_header != webhook_secret:
                logger.warning("Unauthorized webhook request - secret mismatch")
                return Response(status_code=403, content="Unauthorized")
        
        # Get update data
        update_data = await request.json()
        logger.info(f"Received update data: {update_data}")
        
        # Create Update object
        update = Update.de_json(update_data, application.bot)
        logger.info(f"Created Update object: {update}")
        
        # Process all updates through the application
        await application.process_update(update)
        
        logger.info("Update processed successfully")
        return Response(status_code=200, content="ok")
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        return Response(status_code=500, content=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {
        "status": "online",
        "bot": "@kitchenadsconfirms_bot",
        "version": "1.0.0"
    }