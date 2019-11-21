from .logger_collection import LoggerCollection as log
from sys import stdout

log().add_logger('MAIN', stdout)
log().add_logger('SOLVER', stdout)
log().add_logger('ANT', stdout)
# log().add_logger('ATTR_DEBUG', stdout)
log().add_logger('PYBULLET', stdout)
log().add_logger('GRAPH_GRASP', stdout)
# log().add_logger('IK', stdout)
# log().add_logger('PHI_DEPOSIT', stdout)

log().log('loggers loaded normally')
