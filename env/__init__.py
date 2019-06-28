import json
import pybullet
import os
import pathlib

from env.robot import Robot
from env.environment import Environment

# присоединиться к серверу при подключении пакета
server_id = pybullet.connect(pybullet.DIRECT)
if server_id > 0:
    print("default pb server already connected")
    pybullet.disconnect(server_id)

def task_json_parse(dct):
    """Добавляет к прочитанному из json словарю значения по умолчанию,
если они не были предоставлены"""
    if not 'pos' in dct:
        dct['pos'] = (.0,.0,.0)
    if not 'orn' in dct:
        dct['orn'] = (0.0, 0.0, 0.0) # rpy
    if not 'eps' in dct:
        dct['eps'] = 1e-4 # 0.1 mm
    if not 'fixed_base' in dct:
        dct['fixed_base'] = True
    if not 'sdf_name' in dct:
        dct['sdf_name'] = None
    if not 'dofs' in dct:
        dct['dofs'] = None
    return dct

def load_task(filename):
    """Загружает параметры задачи из json-файла filename"""
    with open(filename, 'r') as fp:
        task_data = json.load(fp, object_hook=task_json_parse)

    # получение путей к urdf и sdf файлам
    
    urdf_filename = filename.parent / pathlib.Path(task_data['urdf_name'])
    print(urdf_filename)
    if task_data['sdf_name'] is None:
        sdf_filename = None
    else:
        sdf_filename = filename.parent / pathlib.Path(task_data['sdf_name'])

    # преобразование считанных из файла RPY углов в кват-н
    q_orn = pybullet.getQuaternionFromEuler(task_data['orn'])

    # создание оберток
    R = Robot(str(urdf_filename),
              task_data['effector_name'],
              task_data['pos'],
              q_orn,
              task_data['fixed_base'],
              task_data['eps'])

    # задание начального состояния звеньев
    if task_data['dofs'] is not None:
        for i, dof in enumerate(R._dofs):
            pybullet.resetJointState(R.id, dof, task_data['dofs'][i])

    E = Environment(None if sdf_filename is None else str(sdf_filename))

    return R, E, task_data['endpoint'], task_data['emp_best']

