from typing import TextIO, Optional
from sys import stdout, stderr


class Logger:
    def __init__(self, name: str, fp: Optional[TextIO] = None):
        self.name = name
        self.fp = fp

    def log(self, message: str):
        if self.fp is not None:
            self.fp.write('[{}] {}\n'
                          .format(self.name, message))

    def __bool__(self):
        return self.fp is not None

    def closeable_fp(self):
        return self.fp != stdout and self.fp != stderr

    def __del__(self):
        if self.closeable_fp() and self.fp is not None:
            self.fp.close()
