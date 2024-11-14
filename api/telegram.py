from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    CallbackContext
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
        
        # Add command handlers
        application.add_handler(CommandHandler("start", bot.simple_bot.start))
        application.add_handler(CommandHandler("help", bot.simple_bot.help_command))
        
        # Add message handler that handles both text and callbacks
        application.add_handler(MessageHandler(
            filters.TEXT | filters.COMMAND | filters.StatusUpdate.ALL, 
            bot.handle_message
        ))
        
        # Initialize and start the application
        await application.initialize()
        
        # Set webhook in production
        if os.getenv('ENVIRONMENT') == 'production':
            webhook_url = os.getenv('WEBHOOK_URL')
            if webhook_url:
                webhook_secret = os.getenv('WEBHOOK_SECRET')
                await application.bot.set_webhook(
                    url=f"{webhook_url}/api/telegram",
                    secret_token=webhook_secret
                )
                logger.info(f"Webhook set to {webhook_url}/api/telegram")
            else:
                logger.error("WEBHOOK_URL not found in environment variables")
        
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
        logger.debug("Received webhook request")
        
        # Verify webhook secret if configured
        webhook_secret = os.getenv("WEBHOOK_SECRET")
        if webhook_secret:
            secret_header = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
            logger.debug(f"Checking webhook secret. Expected: {webhook_secret}, Received: {secret_header}")
            if secret_header != webhook_secret:
                logger.warning("Unauthorized webhook request - secret mismatch")
                return Response(status_code=403, content="Unauthorized")
        
        # Get update data
        update_data = await request.json()
        logger.debug(f"Received update data: {update_data}")
        
        # Create Update object
        update = Update.de_json(update_data, application.bot)
        logger.debug(f"Created Update object: {update}")
        
        # Handle update based on type
        if update.callback_query:
            logger.debug("Processing callback query")
            # Route to appropriate bot based on original message
            flow_type, text = await bot.router.route_message(update, CallbackContext(application))
            if flow_type == 'simple':
                await bot.simple_bot.handle_callback(update, CallbackContext(application))
            else:
                await bot.complex_bot.handle_callback(update, CallbackContext(application))
        else:
            # Process regular messages through application
            logger.debug("Processing regular message")
            await application.process_update(update)
        
        logger.debug("Update processed successfully")
        return Response(status_code=200, content="ok")
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        return Response(status_code=500, content=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy"}