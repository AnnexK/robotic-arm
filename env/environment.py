import pybullet as pb
from .robot import Robot

from typing import List, Optional
from .types import Vector3
from .taskdata import TaskData


class Environment:
    """Обертка над объектами pybullet, содержащая информацию
об объектах внешней среды и предназначенная для хранения информации
и удобного освобождения ресурсов"""
    def __init__(self, render: bool, fallback: bool):
        """Параметры:
filename -- имя SDF-файла (абсолютный путь)
при отсутствии параметра создается пустая внешняя среда"""
        self.s: int = pb.connect( #type: ignore
            pb.GUI if render else pb.DIRECT, #type: ignore
            options='--opengl2' if fallback else ''
        )
        self._ids: List[int] = list()

        self.endpoint_obj: int = -1
        self.endpoint: Vector3 = (0.0, 0.0, 0.0)
        self._robot: Optional[Robot] = None

    def __del__(self):
        """Предназначено для освобождения ресурсов"""
        self._remove_bodies()
        pb.disconnect(self.s) #type: ignore

    def _remove_bodies(self):
        for i in self._ids:
            pb.removeBody(i, physicsClientId=self.s) #type: ignore
        self._ids.clear()
        if self.endpoint_obj >= 0:
            pb.removeBody(self.endpoint_obj, physicsClientId=self.s) #type: ignore
            self.endpoint_obj = -1
        self._robot = None
    
    def __bool__(self) -> bool:
        return self._robot is not None
    
    def load_task(self, td: TaskData):
        self._remove_bodies()
        if td.sdf:
            try:
                self._ids = list(pb.loadSDF(td.sdf, #type: ignore
                                            physicsClientId=self.s))
            except pb.error: #type: ignore
                raise ValueError('failed to read SDF file')

        self.endpoint_obj = self.set_endpoint(td.target_pos)
        self.endpoint: Vector3 = td.target_pos
        self._robot = Robot(self.s, td)
    
    def set_endpoint(self, p: Vector3) -> int:
        visual: int = pb.createVisualShape(shapeType=pb.GEOM_SPHERE, #type: ignore
                                           radius=0.05,
                                           rgbaColor=[1., 0., 0., 1.], physicsClientId=self.s)
        mb: int = pb.createMultiBody(baseVisualShapeIndex=visual, #type: ignore
                                     basePosition=p, physicsClientId=self.s)
        return mb

    @property
    def robot(self) -> Optional[Robot]:
        return self._robot

    @property
    def target(self) -> Vector3:
        return self.endpoint
