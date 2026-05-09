import time


def retry(func, retries=3, delay=1):
    """
    Generic retry utility for handling temporary/transient failures.

    Purpose:
    - Automatically retries unstable operations
    - Improves resilience of API/network calls
    - Reduces failures caused by temporary issues

    Common Use Cases:
    - CRM API requests
    - Database operations
    - External service calls
    - Network timeouts
    - Rate-limit recovery

    Example:
        result = retry(
            lambda: api_client.fetch_data(),
            retries=3,
            delay=2
        )

    Retry Strategy:
    Uses simple linear backoff:
        delay * (attempt + 1)

    Example timing:
        Attempt 1 → wait 1 sec
        Attempt 2 → wait 2 sec
        Attempt 3 → final failure
    """

    # --------------------------------------------------
    # Retry loop
    # --------------------------------------------------
    for attempt in range(retries):

        try:
            # Attempt operation execution
            return func()

        except Exception as e:

            # --------------------------------------------------
            # Final retry failed
            #
            # Re-raise original exception so caller
            # can properly handle/log it.
            # --------------------------------------------------
            if attempt == retries - 1:
                raise e

            # --------------------------------------------------
            # Wait before retrying
            #
            # Simple increasing backoff:
            # 1s → 2s → 3s ...
            #
            # Helps reduce:
            # - API overload
            # - transient failures
            # - temporary rate limits
            # --------------------------------------------------
            time.sleep(delay * (attempt + 1))