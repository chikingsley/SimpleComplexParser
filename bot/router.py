from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum, auto
import logging
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Change from INFO to DEBUG

class DataFormat(Enum):
    STRUCTURED = auto()    # data.md format (TIER1-Genio-SG...)
    UNSTRUCTURED = auto()  # data copy.md format (Partner: X, GEO: Y...)
    UNKNOWN = auto()

@dataclass
class FormatDetectionResult:
    format_type: DataFormat
    confidence: float
    sample_matches: list[str]

class DealRouter:
    """Enhanced DealRouter with format detection and state management"""
    
    # Simple patterns to detect structured format
    STRUCTURED_PATTERNS = [
        r'^(?:TIER[123]|NORDICS|LATAM|BALTICS)-',  # Starts with region and dash
        r'^[^-]+-[^-]+-[^-]+-[^-]+-[^-]+-[^-]+-[^-]+-[^-]+-[^-]+-[^-]+-[^-]+'  # Has 11 parts connected by dashes
    ]
    
    # Complex format always starts with "Partner: "
    COMPLEX_START_PATTERN = r'^Partner:\s*([^\n]+)'

    @classmethod
    def detect_format(cls, text: str) -> FormatDetectionResult:
        """Simple format detection based on message structure"""
        if not text:
            return FormatDetectionResult(
                format_type=DataFormat.UNKNOWN,
                confidence=0.0,
                sample_matches=[]
            )
            
        # Skip processing messages
        if "Deal Parsing Progress" in text or "Processing deal" in text:
            return FormatDetectionResult(
                format_type=DataFormat.UNKNOWN,
                confidence=0.0,
                sample_matches=[]
            )
            
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            return FormatDetectionResult(
                format_type=DataFormat.UNKNOWN,
                confidence=0.0,
                sample_matches=[]
            )
            
        # Check if it's a complex format (starts with Partner:)
        if re.match(cls.COMPLEX_START_PATTERN, lines[0], re.IGNORECASE):
            logger.debug("Detected complex format (starts with Partner:)")
            return FormatDetectionResult(
                format_type=DataFormat.UNSTRUCTURED,
                confidence=1.0,
                sample_matches=[lines[0]]
            )
            
        # Check if all lines match structured format
        structured_matches = []
        for line in lines:
            if any(re.match(pattern, line, re.IGNORECASE) for pattern in cls.STRUCTURED_PATTERNS):
                structured_matches.append(line)
        
        if structured_matches and len(structured_matches) == len(lines):
            logger.debug("Detected structured format (matches dash pattern)")
            return FormatDetectionResult(
                format_type=DataFormat.STRUCTURED,
                confidence=1.0,
                sample_matches=structured_matches[:5]
            )
            
        # If neither format matches
        return FormatDetectionResult(
            format_type=DataFormat.UNKNOWN,
            confidence=0.0,
            sample_matches=[]
        )

    @staticmethod
    async def route_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Tuple[str, Optional[str]]:
        """Enhanced message routing with better callback handling"""
        # For callbacks (button clicks)
        if update.callback_query:
            logger.info(f"Processing callback query: {update.callback_query.data}")
            
            # Always route callbacks to complex handler for better compatibility
            return 'complex', None
        
        # For new messages
        if not update.message or not update.message.text:
            logger.warning("No message text found")
            return 'invalid', None
            
        text = update.message.text.strip()
        if not text:
            logger.warning("Empty message text")
            return 'invalid', None

        # Check if we're in edit mode by looking at user data
        user_data = context.user_data
        if user_data and user_data.get('editing_state'):
            logger.info("User is in edit mode, routing to complex flow")
            return 'complex', text
        
        # Detect format for new messages
        detection_result = DealRouter.detect_format(text)
        logger.info(f"Format detection result: {detection_result}")
        
        if detection_result.format_type == DataFormat.STRUCTURED:
            logger.info(f"Routing to simple flow: {text}")
            return 'simple', text
        elif detection_result.format_type == DataFormat.UNSTRUCTURED:
            logger.info(f"Routing to complex flow: {text}")
            return 'complex', text
        else:
            logger.info("Invalid format detected")
            return 'invalid', None

    @staticmethod
    def is_formatted_deal(text: str) -> bool:
        """Check if text matches any deal format"""
        if not text:
            return False
            
        detection_result = DealRouter.detect_format(text)
        # Consider both structured and unstructured as valid formats
        return detection_result.format_type in [DataFormat.STRUCTURED, DataFormat.UNSTRUCTURED]

    @staticmethod
    def get_callback_type(callback_data: str) -> str:
        """Helper to identify callback button type"""
        if not callback_data:
            return 'unknown'
            
        if callback_data.startswith(('approve_', 'reject_')):
            return 'action'
        elif callback_data.startswith(('edit_', 'editfield_')):
            return 'edit'
        elif callback_data.startswith(('next_', 'prev_')):
            return 'navigation'
        elif callback_data.startswith('back_'):
            return 'back'
        else:
            return 'unknown'