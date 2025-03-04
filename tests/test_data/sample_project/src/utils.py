"""Utility functions for sample project."""
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


def format_currency(amount: float) -> str:
    """Format a currency amount."""
    return f"${amount:.2f}"


def timestamp() -> str:
    """Get current timestamp as ISO format string."""
    return datetime.now().isoformat()


def log_event(event_type: str, data: Dict[str, Any]) -> None:
    """Log an event with timestamp."""
    event = {
        "type": event_type,
        "timestamp": timestamp(),
        "data": data
    }
    logger.info(f"Event: {json.dumps(event)}")


def filter_dict(data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """Filter a dictionary to only include certain keys."""
    return {k: v for k, v in data.items() if k in keys}


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get a value from a dictionary."""
    parts = key.split('.')
    result = data
    
    try:
        for part in parts:
            result = result[part]
        return result
    except (KeyError, TypeError):
        return default