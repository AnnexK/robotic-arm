from .logger import Logger
from .singleton import Singleton
from sys import stderr
from typing import TextIO


class LoggerCollection(metaclass=Singleton):
    def __init__(self):
        self.slog_name = 'lc_system'
        self.loggers = {self.slog_name: Logger(self.slog_name,
                                               stderr)}

    def add_logger(self, name: str, fp: TextIO):
        if name in self.loggers and self[name]:
            self.log('logger "{}" already exists'
                     .format(name))
        else:
            if name in self.loggers and not self[name]:
                self.log('replacing dummy logger "{}"'
                         .format(name))
            self.loggers[name] = Logger(name, fp)

    def remove_logger(self, name: str):
        if name in self.loggers:
            del self.loggers[name]
        else:
            self.log('logger "{}" not found'
                     .format(name))

    def log(self, message: str):
        self.loggers[self.slog_name].log(message)

    def __getitem__(self, name: str):
        if name not in self.loggers:
            self.log('creating dummy logger "{}"'
                     .format(name))
            self.loggers[name] = Logger(name)
        return self.loggers[name]
