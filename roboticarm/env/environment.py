from typing import List, Optional

import pybullet as pb
from .robot import Robot


from .types import Vector3
from .taskdata import TaskData


class Environment:
    """
    Обертка над объектами pybullet, содержащая информацию
    об объектах внешней среды и предназначенная для хранения информации
    и удобного освобождения ресурсов.

    :param render: Включать ли отрисовку внешней среды.
    :param fallback: Использовать ли рендер OpenGL 2.
    """

    def __init__(self, render: bool, fallback: bool):
        self.s: int = pb.connect(
            pb.GUI if render else pb.DIRECT, options="--opengl2" if fallback else ""
        )
        self._ids: List[int] = list()

        self.endpoint_obj: int = -1
        self.endpoint: Vector3 = (0.0, 0.0, 0.0)
        self._robot: Optional[Robot] = None

    def _remove_bodies(self):
        for i in self._ids:
            pb.removeBody(i, physicsClientId=self.s)
        self._ids.clear()
        if self.endpoint_obj >= 0:
            pb.removeBody(self.endpoint_obj, physicsClientId=self.s)
            self.endpoint_obj = -1
        self._robot = None

    def __bool__(self) -> bool:
        return self._robot is not None

    def load_task(self, td: TaskData):
        self._remove_bodies()
        if td.sdf:
            try:
                self._ids = list(pb.loadSDF(str(td.sdf), physicsClientId=self.s))
            except pb.error:
                raise ValueError("failed to read SDF file")

        self.endpoint_obj = self.set_endpoint(td.target_pos)
        self.endpoint = td.target_pos
        self._robot = Robot(self.s, td)

    def set_endpoint(self, p: Vector3) -> int:
        visual: int = pb.createVisualShape(
            shapeType=pb.GEOM_SPHERE,
            radius=0.05,
            rgbaColor=[1.0, 0.0, 0.0, 1.0],
            physicsClientId=self.s,
        )
        mb: int = pb.createMultiBody(
            baseVisualShapeIndex=visual,
            basePosition=p,
            physicsClientId=self.s,
        )
        return mb

    @property
    def robot(self) -> Optional[Robot]:
        return self._robot

    @property
    def target(self) -> Vector3:
        return self.endpoint
