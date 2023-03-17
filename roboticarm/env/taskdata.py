from typing import Dict, Any, Optional
from .types import Vector3, State
import pathlib


class TaskDataError(Exception):
    pass


class TaskData:
    def __init__(self, dct: Dict[str, Any]):
        try:
            self.urdf: str = str(pathlib.Path(dct['urdf_name']).resolve().absolute())
            self.sdf: str = dct.get('sdf_name', '')
            if self.sdf:
                self.sdf = str(pathlib.Path(self.sdf).resolve().absolute())
            self.effector = dct['effector_name']
            self.target_pos: Vector3 = dct['endpoint']
            self.pos: Vector3 = dct.get('pos', (.0, .0, .0))
            self.orn: Vector3 = dct.get('orn', (.0, .0, .0))
            self.fixed: bool = dct.get('fixed_base', True)
            self.eps: float = dct.get('eps', 1e-4)
            s = dct.get('dofs', None)
            self.init_state: Optional[State] = None if s is None else tuple(s)
        except KeyError as k:
            raise TaskDataError(f'Task data invalid: {k.args}')


def task_json_parse(dct: Dict[str, Any]):
    """Добавляет к прочитанному из json словарю значения по умолчанию,
если они не были предоставлены"""
    return TaskData(dct)
