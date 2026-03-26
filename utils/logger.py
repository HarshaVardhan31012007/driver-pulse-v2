# Driver Pulse - Logging System
# Comprehensive logging configuration and utilities

import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
import json


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                          'pathname', 'filename', 'module', 'lineno', 
                          'funcName', 'created', 'msecs', 'relativeCreated', 
                          'thread', 'threadName', 'processName', 'process',
                          'getMessage', 'exc_info', 'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry)


class DriverPulseLogger:
    """Enhanced logger for Driver Pulse application."""
    
    def __init__(self, name: str, config_path: Optional[Path] = None):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Setup handlers
        self._setup_console_handler()
        self._setup_file_handler(config_path)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def _setup_console_handler(self):
        """Setup console handler with colored output."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Use colored formatter for console
        console_formatter = ColoredFormatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self, config_path: Optional[Path] = None):
        """Setup file handler with JSON formatting."""
        # Import here to avoid circular imports
        sys.path.append(str(Path(__file__).parent.parent))
        from utils.config import config
        
        # Create logs directory if it doesn't exist
        config.LOGS_PATH.mkdir(parents=True, exist_ok=True)
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = config.LOGS_PATH / f"{self.name}_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Use JSON formatter for files
        json_formatter = JSONFormatter()
        file_handler.setFormatter(json_formatter)
        
        self.logger.addHandler(file_handler)
    
    def debug(self, message, **kwargs):
        """Log debug message with extra data."""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message, **kwargs):
        """Log info message with extra data."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message, **kwargs):
        """Log warning message with extra data."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message, **kwargs):
        """Log error message with extra data."""
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message, **kwargs):
        """Log critical message with extra data."""
        self.logger.critical(message, extra=kwargs)
    
    def exception(self, message, **kwargs):
        """Log exception with traceback."""
        self.logger.exception(message, extra=kwargs)
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics."""
        self.info(f"Performance: {operation}", 
                 operation=operation, 
                 duration=duration, 
                 **kwargs)
    
    def log_data_processing(self, stage: str, records_processed: int, **kwargs):
        """Log data processing metrics."""
        self.info(f"Data Processing: {stage}", 
                 stage=stage, 
                 records_processed=records_processed, 
                 **kwargs)
    
    def log_error_with_context(self, error: Exception, context: dict, **kwargs):
        """Log error with additional context."""
        self.error(f"Error in {context.get('operation', 'unknown')}: {str(error)}",
                  error_type=type(error).__name__,
                  error_message=str(error),
                  context=context,
                  **kwargs)


# Logger factory
def get_logger(name: str) -> DriverPulseLogger:
    """Get a configured logger instance."""
    return DriverPulseLogger(name)


# Performance monitoring decorator
def log_performance(logger_name: str = None):
    """Decorator to log function performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)
            
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                
                logger.log_performance(
                    operation=f"{func.__module__}.{func.__name__}",
                    duration=duration,
                    success=True
                )
                
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                
                logger.log_error_with_context(
                    error=e,
                    context={
                        'operation': f"{func.__module__}.{func.__name__}",
                        'duration': duration,
                        'args_count': len(args),
                        'kwargs_keys': list(kwargs.keys())
                    }
                )
                
                raise
        
        return wrapper
    return decorator


# Context manager for performance logging
class PerformanceLogger:
    """Context manager for performance logging."""
    
    def __init__(self, operation: str, logger_name: str = None):
        self.operation = operation
        self.logger = get_logger(logger_name or __name__)
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.log_performance(
                operation=self.operation,
                duration=duration,
                success=True
            )
        else:
            self.logger.log_error_with_context(
                error=exc_val,
                context={
                    'operation': self.operation,
                    'duration': duration
                }
            )


# Global logger instances
main_logger = get_logger("main")
data_logger = get_logger("data_processing")
signal_logger = get_logger("signal_processing")
earnings_logger = get_logger("earnings_forecast")
dashboard_logger = get_logger("dashboard")


def setup_logging(config_dict: dict = None):
    """Setup logging configuration from dictionary."""
    if config_dict is None:
        # Default configuration
        config_dict = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                }
            },
            'handlers': {
                'default': {
                    'level': 'INFO',
                    'formatter': 'standard',
                    'class': 'logging.StreamHandler',
                }
            },
            'loggers': {
                '': {
                    'handlers': ['default'],
                    'level': 'INFO',
                    'propagate': False
                }
            }
        }
    
    logging.config.dictConfig(config_dict)


# Export main logger for easy access
__all__ = [
    'get_logger',
    'log_performance',
    'PerformanceLogger',
    'main_logger',
    'data_logger',
    'signal_logger',
    'earnings_logger',
    'dashboard_logger',
    'setup_logging'
]
