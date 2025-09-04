"""
Logging utility functions.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
) -> None:
    """Setup logging configuration."""
    
    # Convert string level to logging level
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Add file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        
        # Get root logger and add file handler
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    # Log setup completion
    logging.info(f"Logging configured with level: {level}")
    if log_file:
        logging.info(f"Log file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)


def log_function_call(func_name: str, args: dict, logger: logging.Logger) -> None:
    """Log function call details for debugging."""
    logger.debug(f"Function call: {func_name} with args: {args}")


def log_function_result(func_name: str, result: any, logger: logging.Logger) -> None:
    """Log function result for debugging."""
    logger.debug(f"Function result: {func_name} returned: {result}")


def log_error(error: Exception, context: str, logger: logging.Logger) -> None:
    """Log error with context information."""
    logger.error(f"Error in {context}: {str(error)}", exc_info=True)
