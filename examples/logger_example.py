"""
Example usage of the async logger in the algo-s project.
This demonstrates various ways to use the logger:
- Basic usage
- Async methods
- Context manager
- Decorator
"""

import asyncio
import random

# Fix import path
import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now import the logger
from src.core.logger import AsyncLogger, default_logger, log_async


# Example 1: Basic usage with default logger
def basic_usage():
    print("\n--- Example 1: Basic Usage ---")
    # These work in both sync and async code
    default_logger.debug("This is a debug message")
    default_logger.info("This is an info message")
    default_logger.warning("This is a warning message")
    default_logger.error("This is an error message")
    default_logger.critical("This is a critical message")


# Example 2: Custom logger with file output
def custom_logger_example():
    print("\n--- Example 2: Custom Logger ---")
    # Create a custom debug-level logger that writes to both console and file
    logger = AsyncLogger(
        name="custom-logger",
        level=10,  # DEBUG level
        log_to_file=True,
        log_dir="logs",
    )

    logger.debug("Debug message from custom logger")
    logger.info("Info message from custom logger")

    # Log with additional data
    extra_data = {"user_id": 123, "action": "login"}
    logger.info(f"User action: {extra_data}")


# Example 3: Async logging methods
async def async_methods_example():
    print("\n--- Example 3: Async Methods ---")
    # Create async tasks
    tasks = []
    for i in range(5):
        # Add a random delay to simulate async operations
        tasks.append(log_operation(i, delay=random.uniform(0.1, 0.5)))

    # Run tasks concurrently
    await asyncio.gather(*tasks)


async def log_operation(task_id, delay):
    """Example async operation with logging"""
    await default_logger.ainfo(f"Task {task_id} started")
    await asyncio.sleep(delay)  # Simulate work
    await default_logger.ainfo(f"Task {task_id} completed after {delay:.2f}s")


# Example 4: Using the context manager
async def context_manager_example():
    print("\n--- Example 4: Context Manager ---")

    # Success case
    async with default_logger as logger:
        await logger.ainfo("Starting operation within context")
        await asyncio.sleep(0.3)  # Simulate work
        await logger.ainfo("Operation in progress...")
        await asyncio.sleep(0.2)  # More work
    # Automatically logs completion time

    # Error case
    try:
        async with default_logger as logger:
            await logger.ainfo("Starting operation that will fail")
            await asyncio.sleep(0.2)
            # Simulate an error
            raise ValueError("Something went wrong!")
    except ValueError:
        print("Error was caught but logger already recorded it")


# Example 5: Using the decorator
@log_async()
async def example_function(param1, param2):
    """Function decorated with log_async"""
    await asyncio.sleep(0.3)  # Simulate work
    if param1 > param2:
        return "Success"
    else:
        raise ValueError("param1 must be greater than param2")


async def decorator_example():
    print("\n--- Example 5: Decorator ---")

    # Success case
    try:
        result = await example_function(10, 5)
        print(f"Function returned: {result}")
    except Exception as e:
        print(f"Error: {e}")

    # Error case
    try:
        result = await example_function(5, 10)  # Will fail
        print(f"Function returned: {result}")
    except Exception as e:
        print(f"Error caught: {e}")


# Run all examples
async def main():
    # Sync examples
    basic_usage()
    custom_logger_example()

    # Async examples
    await async_methods_example()
    await context_manager_example()
    await decorator_example()


if __name__ == "__main__":
    asyncio.run(main())
