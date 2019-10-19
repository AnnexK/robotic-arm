from .logger_collection import LoggerCollection as log
from sys import stdout


log().add_logger('ANT', stdout)
