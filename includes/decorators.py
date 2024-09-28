import time
from functools import wraps
from typing import Any, Callable, Type, Union
from includes.logging_config import get_logger

logger = get_logger(__name__)

def retry(exceptions: Union[Type[Exception], tuple[Type[Exception], ...]], 
          tries: int = 3, 
          delay: int = 1, 
          backoff: int = 2, 
          logger: Any = None):
    """
    Retry decorator with exponential backoff.
    
    Args:
    exceptions: Exception or tuple of exceptions to catch
    tries: Number of times to try (not retry) before giving up
    delay: Initial delay between retries in seconds
    backoff: Backoff multiplier e.g. value of 2 will double the delay each retry
    logger: Logger to use. If None, print.
    """
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            # Extract retry-specific kwargs
            mtries = kwargs.pop('_retry_tries', tries)
            mdelay = kwargs.pop('_retry_delay', delay)
            mbackoff = kwargs.pop('_retry_backoff', backoff)
            _exceptions = kwargs.pop('_retry_exceptions', exceptions)
            
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except _exceptions as e:
                    msg = f"{str(e)}, Retrying in {mdelay} seconds..."
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= mbackoff
            return f(*args, **kwargs)
        return f_retry
    return deco_retry