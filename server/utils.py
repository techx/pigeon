"""Utils for server functions."""

import inspect

BLUE = "\033[34m"
RESET = "\033[0m"


def custom_log(*args):
    """Prints some calling information along with logging info."""
    frame = inspect.currentframe()
    caller_frame = inspect.getouterframes(frame)[1]
    file_name = caller_frame.filename
    function_name = caller_frame.function
    print(f"{BLUE}{file_name}/{function_name}{RESET}", *args)
