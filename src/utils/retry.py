"""
Retry - Operation retry and timeout control
"""

import time
from typing import Callable, Any, Optional
from functools import wraps
from loguru import logger


def retry_operation(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying operations with exponential backoff.
    
    Args:
        max_retries: Maximum number of retries
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(
                            f"Operation failed after {max_retries} retries: {e}"
                        )
                        raise
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                        f"Retrying in {current_delay:.1f}s..."
                    )
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
        
        return wrapper
    
    return decorator


def retry_with_timeout(
    operation: Callable,
    timeout: float,
    interval: float = 0.5,
    *args,
    **kwargs
) -> Any:
    """
    Retry operation until success or timeout.
    
    Args:
        operation: Function to execute
        timeout: Maximum time in seconds
        interval: Time between attempts
        *args: Positional arguments for operation
        **kwargs: Keyword arguments for operation
        
    Returns:
        Operation result
        
    Raises:
        TimeoutError: If timeout exceeded
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            return operation(*args, **kwargs)
        except Exception as e:
            logger.debug(f"Operation failed: {e}")
            time.sleep(interval)
    
    raise TimeoutError(f"Operation timed out after {timeout} seconds")


def wait_for_condition(
    condition: Callable[[], bool],
    timeout: float = 30.0,
    interval: float = 0.5,
    error_message: str = "Condition not met within timeout"
) -> bool:
    """
    Wait for condition to be true.
    
    Args:
        condition: Condition function to check
        timeout: Maximum wait time in seconds
        interval: Time between checks
        error_message: Error message on timeout
        
    Returns:
        True if condition met
        
    Raises:
        TimeoutError: If timeout exceeded
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if condition():
            logger.info("Condition met")
            return True
        
        time.sleep(interval)
    
    logger.error(error_message)
    raise TimeoutError(error_message)