import sys
import time


class LineSleep:
    def __init__(self, duration: float, current_frame, print_=False):
        def _sleep(frame, event, arg):
            if event == "line":
                if current_frame in str(frame):
                    time.sleep(duration)
                    if print_:
                        print(frame)
            return _sleep

        self.func = _sleep

    def __enter__(self):
        sys.settrace(self.func)
        return self

    def __exit__(self, ext_type, exc_value, traceback):
        sys.settrace(None)
