"""
Contains a very simple performance timer,
which can be used with the Python 3 `with` construct,
making it very easy to time how long a piece of code takes to run.
"""
import time
import types
from typing import Optional, Type

class Timer:
    """
    A very simple performance timer,
    which can be used with the Python 3 `with` construct,
    making it very easy to time how long a piece of code takes to run.
    """

    def __init__(self, taskName:str):
        self._task_name = taskName
        self._start_time = float('nan')

    def __enter__(self):
        self._start_time = time.time()

    def __exit__(self,
                _exception_type: Optional[Type[BaseException]],
                _excception_instance: Optional[BaseException],
                _exception_traceback: Optional[types.TracebackType]) -> bool:
        end_time = time.time()
        total_time_ms = int( (end_time - self._start_time) * 1000 )
        print(f"{self._task_name} took {total_time_ms}ms")
        return False # We don't handle the exception
