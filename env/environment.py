import pybullet as pb
from .robot import Robot

from typing import List
from .types import Vector3
from .taskdata import TaskData


class Environment:
    """Обертка над объектами pybullet, содержащая информацию
об объектах внешней среды и предназначенная для хранения информации
и удобного освобождения ресурсов"""
    def __init__(self, render: bool, fallback: bool, td: TaskData):
        """Параметры:
filename -- имя SDF-файла (абсолютный путь)
при отсутствии параметра создается пустая внешняя среда"""
        self.s: int = pb.connect( #type: ignore
            pb.GUI if render else pb.DIRECT, #type: ignore
            options='--opengl2' if fallback else ''
        )
        if not td.sdf:
            self._ids: List[int] = list()  # пустой
        else:
            try:
                self._ids = pb.loadSDF(td.sdf, #type: ignore
                                       physicsClientId=self.s)
            except pb.error: #type: ignore
                raise ValueError('failed to read SDF file')

        self.endpoint_obj: int = self.set_endpoint(td.target_pos)
        self.endpoint: Vector3 = td.target_pos
        self._robot = Robot(self.s, td)

    def __del__(self):
        """Предназначено для освобождения ресурсов"""
        for i in self._ids:
            pb.removeBody(i) #type: ignore
        pb.removeBody(self.endpoint_obj) #type: ignore
        del self._robot
        pb.disconnect(self.s) #type: ignore

    def set_endpoint(self, p: Vector3) -> int:
        visual: int = pb.createVisualShape(shapeType=pb.GEOM_SPHERE, #type: ignore
                                           radius=0.05,
                                           rgbaColor=[1., 0., 0., 1.])
        mb: int = pb.createMultiBody(baseVisualShapeIndex=visual, #type: ignore
                                     basePosition=p)
        return mb

    @property
    def robot(self) -> Robot:
        return self._robot

    @property
    def target(self) -> Vector3:
        return self.endpoint
