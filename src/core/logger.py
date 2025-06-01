"""
Asynchronous logger for the algo-s project.
Provides logging capabilities with async support.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from functools import wraps
from typing import Optional, Callable


class AsyncLogger:
    """
    Asynchronous logger that supports both sync and async logging operations.
    Provides standard logging levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
    """

    def __init__(
        self,
        name: str = "algo-s",
        level: int = logging.INFO,
        log_to_file: bool = False,
        log_dir: str = "logs",
        log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    ):
        """
        Initialize the async logger.

        Args:
            name: Logger name
            level: Logging level
            log_to_file: Whether to log to file
            log_dir: Directory for log files
            log_format: Format for log messages
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.log_format = log_format

        # Configure console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(log_format))
        self.logger.addHandler(console_handler)

        # Configure file handler if requested
        if log_to_file:
            os.makedirs(log_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(log_dir, f"{name}_{timestamp}.log")
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter(log_format))
            self.logger.addHandler(file_handler)

        # Event loop for async operations
        self.loop = (
            asyncio.get_event_loop() if asyncio.get_event_loop().is_running() else None
        )

    def _log_async(self, level: int, msg: str, *args, **kwargs) -> None:
        """Internal method to handle async logging"""
        if not self.loop or not self.loop.is_running():
            # Fallback to sync logging if no event loop is running
            self.logger.log(level, msg, *args, **kwargs)
            return

        # Create a task for logging to avoid blocking
        asyncio.create_task(self._log_coro(level, msg, *args, **kwargs))

    async def _log_coro(self, level: int, msg: str, *args, **kwargs) -> None:
        """Coroutine for actual logging operation"""
        # Use run_in_executor to avoid blocking the event loop
        await asyncio.get_event_loop().run_in_executor(
            None, lambda: self.logger.log(level, msg, *args, **kwargs)
        )

    # Standard logging methods (sync)
    def debug(self, msg: str, *args, **kwargs) -> None:
        """Log a debug message"""
        self._log_async(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        """Log an info message"""
        self._log_async(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        """Log a warning message"""
        self._log_async(logging.WARNING, msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        """Log an error message"""
        self._log_async(logging.ERROR, msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        """Log a critical message"""
        self._log_async(logging.CRITICAL, msg, *args, **kwargs)

    # Async logging methods
    async def adebug(self, msg: str, *args, **kwargs) -> None:
        """Log a debug message asynchronously"""
        await self._log_coro(logging.DEBUG, msg, *args, **kwargs)

    async def ainfo(self, msg: str, *args, **kwargs) -> None:
        """Log an info message asynchronously"""
        await self._log_coro(logging.INFO, msg, *args, **kwargs)

    async def awarning(self, msg: str, *args, **kwargs) -> None:
        """Log a warning message asynchronously"""
        await self._log_coro(logging.WARNING, msg, *args, **kwargs)

    async def aerror(self, msg: str, *args, **kwargs) -> None:
        """Log an error message asynchronously"""
        await self._log_coro(logging.ERROR, msg, *args, **kwargs)

    async def acritical(self, msg: str, *args, **kwargs) -> None:
        """Log a critical message asynchronously"""
        await self._log_coro(logging.CRITICAL, msg, *args, **kwargs)

    # Context manager for logging execution time
    async def __aenter__(self):
        """Enter async context manager"""
        self.start_time = datetime.now()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager and log execution time"""
        elapsed = datetime.now() - self.start_time
        if exc_type:
            await self.aerror(
                f"Operation failed after {elapsed.total_seconds():.2f}s: {exc_val}"
            )
            return False
        await self.ainfo(
            f"Operation completed successfully in {elapsed.total_seconds():.2f}s"
        )
        return True


# Create a function decorator for logging
def log_async(logger: Optional[AsyncLogger] = None):
    """
    Decorator for logging async function calls.

    Args:
        logger: AsyncLogger instance to use, or None to create a new one
    """

    def decorator(func: Callable):
        nonlocal logger
        if logger is None:
            logger = AsyncLogger(name=func.__module__)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger.info(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            try:
                start_time = datetime.now()
                result = await func(*args, **kwargs)
                elapsed = datetime.now() - start_time
                logger.info(
                    f"{func.__name__} completed in {elapsed.total_seconds():.2f}s"
                )
                return result
            except Exception as e:
                logger.error(f"{func.__name__} failed: {str(e)}")
                raise

        return wrapper

    return decorator


# Default logger instance
default_logger = AsyncLogger()
