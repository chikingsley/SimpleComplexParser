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
    
    # Structured format patterns (data.md)
    STRUCTURED_PATTERNS = [
        r'^(?:TIER[123]|NORDICS|LATAM)-[\w]+-[A-Z]{2}(?:\|[A-Z]{2})*-[\w\s]+?-[\w\s|]+?-cpa(?:_crg)?-\d+(?:\.\d+)?-[\d.]+?-[&\w\s|]+?-[&\w\s]+?-[&\w\s]+$',
    ]
    
    # Unstructured format patterns (data copy.md)
    UNSTRUCTURED_PATTERNS = [
        r'(?:Partner|GEO):\s*([^\n]+)',
        r'Source:\s*([^\n]+)',
        r'CPA\s*\+\s*crg\s*:\s*(\d+)\$\s*\+\s*(\d+)%',
        r'Landing Page:\s*([^\n]+)',
    ]
    
    # Deal indicators for validation
    DEAL_INDICATORS = {
        'strong': [
            r"\d+\s*\+\s*\d+%",          # 1000+10%
            r"\$?\s*\d+\s*\+\s*\d+%",    # $1000+10%
            r"(?:Price|CPA|CPL)\s*:?\s*[\d.]+",
            r"(?:Partner|Company)\s*:",
            r"(?:GEO|Country)\s*:"
        ],
        'supporting': [
            r"Source\s*:",
            r"Funnel(?:s)?\s*:",
            r"Landing Page\s*:",
            r"model\s*:",
            r"[A-Z]{2}\s*(?:native|eng|fr|es|de)",
            r"(?:FB|Facebook|Google|SEO|Taboola|Native)\s+[Tt]raffic"
        ]
    }

    @classmethod
    def detect_format(cls, text: str) -> FormatDetectionResult:
        """Enhanced format detection with confidence scoring"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Skip processing messages
        if "Deal Parsing Progress" in text or "Processing deal" in text:
            return FormatDetectionResult(
                format_type=DataFormat.UNKNOWN,
                confidence=0.0,
                sample_matches=[]
            )
        
        # Match patterns
        structured_matches = []
        unstructured_matches = []
        
        for line in lines:
            # Check structured format
            for pattern in cls.STRUCTURED_PATTERNS:
                if re.match(pattern, line, re.IGNORECASE):
                    structured_matches.append(line)
                    break
                    
        # Check unstructured format
        text_chunk = '\n'.join(lines)
        for pattern in cls.UNSTRUCTURED_PATTERNS:
            matches = re.findall(pattern, text_chunk, re.IGNORECASE | re.MULTILINE)
            unstructured_matches.extend([m if isinstance(m, str) else m[0] for m in matches])
        
        # Check deal indicators
        strong_matches = sum(1 for pattern in cls.DEAL_INDICATORS['strong']
                           if re.search(pattern, text_chunk, re.IGNORECASE))
        supporting_matches = sum(1 for pattern in cls.DEAL_INDICATORS['supporting']
                               if re.search(pattern, text_chunk, re.IGNORECASE))
        
        # Calculate confidence scores
        structured_score = len(structured_matches) / len(lines) if lines else 0
        unstructured_score = len(unstructured_matches) / (len(lines) * 2) if lines else 0
        indicator_score = (strong_matches + (supporting_matches * 0.5)) / (
            len(cls.DEAL_INDICATORS['strong']) + (len(cls.DEAL_INDICATORS['supporting']) * 0.5)
        )
        
        logger.debug(f"Format detection scores - Structured: {structured_score:.2f}, "
                    f"Unstructured: {unstructured_score:.2f}, Indicators: {indicator_score:.2f}")
        
        # Determine format
        if structured_score > 0.7:
            return FormatDetectionResult(
                format_type=DataFormat.STRUCTURED,
                confidence=structured_score + (indicator_score * 0.2),
                sample_matches=structured_matches[:5]
            )
        elif (unstructured_score > 0.3 and indicator_score > 0.3) or indicator_score > 0.5:
            return FormatDetectionResult(
                format_type=DataFormat.UNSTRUCTURED,
                confidence=unstructured_score + (indicator_score * 0.3),
                sample_matches=unstructured_matches[:5]
            )
        else:
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
            
            # Get original message if it exists
            original_message = update.callback_query.message.reply_to_message
            
            # If we have original message text, detect its format
            if original_message and original_message.text:
                detection_result = DealRouter.detect_format(original_message.text)
                logger.info(f"Callback original message format: {detection_result.format_type}")
                
                if detection_result.format_type == DataFormat.STRUCTURED:
                    return 'simple', original_message.text
                elif detection_result.format_type == DataFormat.UNSTRUCTURED:
                    return 'complex', original_message.text
            
            # If no original message or couldn't detect format, default to complex
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