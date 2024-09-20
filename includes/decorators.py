import time
from functools import wraps
from includes.logging_config import get_logger

logger = get_logger(__name__)

def retry(exceptions, tries=3, delay=1, backoff=2, logger=None):
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
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    msg = f"{str(e)}, Retrying in {mdelay} seconds..."
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)
        return f_retry
    return deco_retry