from typing import TextIO
from sys import stdout, stderr


class Logger:
    def __init__(self, name, fp: TextIO = None):
        self.name = name
        self.fp = fp

    def log(self, message):
        if self.fp is not None:
            self.fp.write('[{}] {}\n'
                          .format(self.name, message))

    def __bool__(self):
        return self.fp is not None

    def closeable_fp(self):
        return self.fp != stdout and self.fp != stderr and self.fp is not None

    def __del__(self):
        if self.closeable_fp():
            self.fp.close()
