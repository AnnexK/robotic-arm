import pybullet as pb
from logger import log
from .robot import Robot


class Environment:
    """Обертка над объектами pybullet, содержащая информацию
об объектах внешней среды и предназначенная для хранения информации
и удобного освобождения ресурсов"""
    def __init__(self, render=True, fallback=False, filename=None):
        """Параметры:
filename -- имя SDF-файла (абсолютный путь)
при отсутствии параметра создается пустая внешняя среда"""
        self.s = pb.connect(pb.GUI if render else pb.DIRECT,
                            options='--opengl2' if fallback else '')
        if filename is None:
            self._ids = list()  # пустой
        else:
            try:
                self._ids = pb.loadSDF(filename,
                                       physicsClientId=self.s)
            except pb.error:
                raise ValueError('failed to read SDF file')

        self.endpoint = -1
        self._robot = None

    def __getitem__(self, i):
        """Возвращает идентификатор PB i-го объекта"""
        return self._ids[i]

    def __del__(self):
        """Предназначено для освобождения ресурсов"""
        for i in self._ids:
            pb.removeBody(i)
        if self.endpoint >= 0:
            pb.removeBody(self.endpoint)
        if self.robot is not None:
            del self._robot
        pb.disconnect(self.s)

    def set_endpoint(self, p):
        visual = pb.createVisualShape(shapeType=pb.GEOM_SPHERE,
                                      radius=0.05,
                                      rgbaColor=[1., 0., 0., 1.])
        self.endpoint = pb.createMultiBody(baseVisualShapeIndex=visual,
                                           basePosition=p)

    @property
    def robot(self):
        return self._robot

    def add_robot(self, **kwargs):
        if self._robot is not None:
            raise ValueError('Robot already present')
        try:
            self._robot = Robot(self.s, **kwargs)
        except KeyError as k:
            raise ValueError('missing required parameter: {}'
                             .format(k.args[0]))
