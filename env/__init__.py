import json
import pathlib

from env.environment import Environment
from logger import log


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


def load_task(filename, render, fallback):
    """Загружает параметры задачи из json-файла filename"""
    with open(filename, 'r') as fp:
        task_data = json.load(fp, object_hook=task_json_parse)

    # получение путей к urdf и sdf файлам

    urdf_filename = filename.parent / pathlib.Path(task_data['urdf_name'])
    if task_data['sdf_name'] is None:
        sdf_filename = None
    else:
        sdf_filename = filename.parent / pathlib.Path(task_data['sdf_name'])

    E = Environment(render,
                    fallback,
                    None if sdf_filename is None
                    else str(sdf_filename))

    E.set_endpoint(task_data['endpoint'])

    E.add_robot(filename=str(urdf_filename),
                eff_name=task_data['effector_name'],
                pos=task_data['pos'],
                orn=task_data['orn'],
                fixed=task_data['fixed_base'],
                kin_eps=task_data['eps'],
                dofs=task_data['dofs'])

    log()['PYBULLET'].log('environment loaded successfully')

    return E, task_data['endpoint'], task_data['emp_best']
