"""
Logging configuration for simulation
"""
import logging
import sys
from typing import Optional

# Configure logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Global logger instance
_logger: Optional[logging.Logger] = None


def get_logger(name: str = "simulation") -> logging.Logger:
    """Get or create logger instance
    
    Args:
        name: Logger name (default: "simulation")
        
    Returns:
        Configured logger instance
    """
    global _logger
    if _logger is None:
        _logger = logging.getLogger(name)
        _logger.setLevel(logging.INFO)
        
        # Create console handler if not exists
        if not _logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
            handler.setFormatter(formatter)
            
            _logger.addHandler(handler)
    
    return _logger


def set_log_level(level: str):
    """Set logging level
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger = get_logger()
    numeric_level = getattr(logging, level.upper(), None)
    if isinstance(numeric_level, int):
        logger.setLevel(numeric_level)
        for handler in logger.handlers:
            handler.setLevel(numeric_level)

