import json

from env.environment import Environment
from .taskdata import TaskData

from logger import log

from .taskdata import TaskData, task_json_parse


def load_task(filename: str, render: bool, fallback: bool) -> Environment:
    """Загружает параметры задачи из json-файла filename"""
    with open(filename, 'r') as fp:
        td: TaskData = json.load(fp, object_hook=task_json_parse)

    E = Environment(render,
                    fallback)
    E.load_task(td)

    log()['PYBULLET'].log('environment loaded successfully')

    return E
