import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional
from pathlib import Path

def setup_logger(
    name: Optional[str] = None,
    max_bytes: int = 1024 * 1024,  # 1MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Configure and return a logger instance with standardized formatting and rotation.
    
    Args:
        name: The name for the logger instance. If None, returns the root logger.
        max_bytes: Maximum size of each log file in bytes before rotation occurs.
        backup_count: Number of backup files to keep.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path('./logs')
    log_dir.mkdir(exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Use a single, shared log file for all modules
    file_handler = RotatingFileHandler(
        log_dir / 'server.log',  # Single log file for all modules
        maxBytes=max_bytes,
        backupCount=backup_count,
        mode='a'  # Changed to append mode
    )
    file_handler.setFormatter(formatter)

    # Get logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Prevent adding handlers multiple times
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger 