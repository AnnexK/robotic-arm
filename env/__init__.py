import json
import pybullet
import pathlib

from env.robot import Robot
from env.environment import Environment

server_type = pybullet.GUI
# присоединиться к серверу при подключении пакета
server_id = pybullet.connect(server_type, options='--opengl2')
if server_id == -1:
    raise RuntimeError('not connected to pb server')

if server_id > 0:
    print("default pb server already connected")
    pybullet.disconnect(server_id)


def task_json_parse(dct):
    """Добавляет к прочитанному из json словарю значения по умолчанию,
если они не были предоставлены"""
    if 'pos' not in dct:
        dct['pos'] = (.0, .0, .0)
    if 'orn' not in dct:
        dct['orn'] = (0.0, 0.0, 0.0)  # rpy
    if 'eps' not in dct:
        dct['eps'] = 1e-4  # 0.1 mm
    if 'fixed_base' not in dct:
        dct['fixed_base'] = True
    if 'sdf_name' not in dct:
        dct['sdf_name'] = None
    if 'dofs' not in dct:
        dct['dofs'] = None
    return dct


def load_task(filename):
    """Загружает параметры задачи из json-файла filename"""
    with open(filename, 'r') as fp:
        task_data = json.load(fp, object_hook=task_json_parse)

    # получение путей к urdf и sdf файлам

    urdf_filename = filename.parent / pathlib.Path(task_data['urdf_name'])
    if task_data['sdf_name'] is None:
        sdf_filename = None
    else:
        sdf_filename = filename.parent / pathlib.Path(task_data['sdf_name'])

    # создание оберток
    R = Robot(str(urdf_filename),
              task_data['effector_name'],
              task_data['pos'],
              task_data['orn'],
              task_data['fixed_base'],
              task_data['eps'])

    # задание начального состояния звеньев
    if task_data['dofs'] is not None:
        R.state = task_data['dofs']

    E = Environment(None if sdf_filename is None else str(sdf_filename))

    return R, E, task_data['endpoint'], task_data['emp_best']
