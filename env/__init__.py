import json
import pathlib

from env.environment import Environment
from .taskdata import TaskData

from logger import log

from .taskdata import TaskData, task_json_parse


def load_task(filename: pathlib.Path, render: bool, fallback: bool) -> Environment:
    """Загружает параметры задачи из json-файла filename"""
    with open(filename, 'r') as fp:
        td: TaskData = json.load(fp, object_hook=task_json_parse)

    # получение путей к urdf и sdf файлам

    td.urdf = str(filename.parent / pathlib.Path(td.urdf))
    if td.sdf:
        td.sdf = str(filename.parent / pathlib.Path(td.sdf))

    E = Environment(render,
                    fallback,
                    td)

    log()['PYBULLET'].log('environment loaded successfully')

    return E
