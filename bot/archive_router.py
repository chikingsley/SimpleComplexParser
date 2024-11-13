import re
import logging
from typing import Tuple, Optional
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class DealRouter:
    @staticmethod
    def is_formatted_deal(text: str) -> bool:
        """Check if text matches the formatted deal pattern"""
        # Log the incoming text for debugging
        logger.debug(f"Checking text: {text}")
        
        # Simplified pattern that matches the core structure
        pattern = r'^TIER[123]-[\w\s]+-[\w\s]+-[\w\s]+-[\w\s|]+-cpa(?:_crg)?-\d+(?:\.\d+)?-[\d.&]+-[&\w\s|]+-[&\w\s]+-[&\w\s]+'
        
        # Check each line of the text
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        for line in lines:
            match = re.match(pattern, line, re.IGNORECASE)
            # Log the match result for debugging
            logger.debug(f"Line: {line}, Match: {bool(match)}")
            if not match:
                return False
        return True

    @staticmethod
    async def route_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Tuple[str, Optional[str]]:
        """Route message to appropriate handler"""
        # For callbacks (button clicks)
        if update.callback_query:
            original_message = update.callback_query.message.reply_to_message
            if original_message and DealRouter.is_formatted_deal(original_message.text):
                logger.info("Routing callback to simple flow")
                return 'simple', original_message.text
            logger.info("Routing callback to complex flow")
            return 'complex', None
        
        # For new messages
        if not update.message or not update.message.text:
            logger.warning("No message text found")
            return 'invalid', None
            
        text = update.message.text.strip()
        if not text:
            logger.warning("Empty message text")
            return 'invalid', None
            
        # Log the routing decision
        is_formatted = DealRouter.is_formatted_deal(text)
        logger.info(f"Message format check: {'formatted' if is_formatted else 'unformatted'}")
        
        if is_formatted:
            logger.info(f"Routing to simple flow: {text}")
            return 'simple', text
        else:
            logger.info(f"Routing to complex flow: {text}")
            return 'complex', text