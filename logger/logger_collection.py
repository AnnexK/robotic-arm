from .logger import Logger
from .singleton import Singleton
from sys import stderr
from typing import TextIO


class LoggerCollection(metaclass=Singleton):
    def __init__(self):
        syslog_name = 'lc_system'
        self.loggers = {syslog_name: Logger(syslog_name, stderr)}

    def add_logger(self, name: str, fp: TextIO):
        if name in self.loggers and self[name]:
            self.loggers['lc_system'].log('Logger "{}" already exists.'
                                          .format(name))
        else:
            self.loggers[name] = Logger(name, fp)

    def remove_logger(self, name: str):
        if name in self.loggers:
            del self.loggers[name]

    def __getitem__(self, name: str):
        if name not in self.loggers:
            self.loggers[name] = Logger(name)
        return self.loggers[name]
