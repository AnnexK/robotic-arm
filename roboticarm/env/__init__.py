from logging import getLogger

from .taskdata import TaskData
from .robot import Robot, State
from .environment import Environment


_logger = getLogger(__name__)


def load_task(filename: str, render: bool, fallback: bool) -> Environment:
    """Загружает параметры задачи из json-файла filename."""
    task_data = TaskData.parse_file(filename)

    env = Environment(render,
                      fallback)
    env.load_task(task_data)

    _logger.debug("Environment loaded successfully")

    return env


__all__ = [
    Robot.__name__,
    State.__name__,
    Environment.__name__,
    TaskData.__name__,
    load_task.__name__,
]
