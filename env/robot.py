import pybullet as pb
from math import isclose
import json
import os

class Robot:
    """Обертка над объектом pybullet, содержащая информацию
об объекте робота и позволяющая производить операции перемещения
рабочего органа, получения информации о положении рабочего
органа и проверки на столкновения"""
    def __init__(self, filename, eff_name, pos, orn, fixed, kin_eps):
        """Параметры:
filename -- имя URDF-файла (абсолютный путь)
eff_name -- имя звена-рабочего органа
pos -- координаты местоположения базового звена
orn -- ориентация базового звена (кватернион)
fixed -- флаг фиксирования положения базы (0/1)
kin_eps -- значение погрешности для решения ОКЗ"""
        # читаем urdf файл
        self._id = pb.loadURDF(filename,
                               basePosition=pos,
                               baseOrientation=orn,
                               flags=pb.URDF_USE_SELF_COLLISION,
                               useFixedBase=fixed)

        self.__kin_eps = kin_eps

        # достаем индекс звена-схвата
        self._eff_id = filter(
            lambda j : j[12].decode() == eff_name,
            [pb.getJointInfo(self._id,i)
             for i in range(pb.getNumJoints(self._id))]
        ).__next__()[0]

        # получаем список индексов звеньев со степенями свободы
        self._dofs = getDOFIds(self._id)
        
    def __del__(self):
        """Предназначено для освобождения ресурсов pybullet"""
        try:
            # удалить объект из pb при уничтожении Robot
            pb.removeBody(self._id)
        except pb.error:
            print("Предупреждение: Нет подключения к серверу")

    # id для доступа средствами pb
    @property
    def id(self):
        return self._id

    # индекс рабочего органа
    @property
    def eff_id(self):
        return self._eff_id

    def move_to(self, pos, orn=None):
        """Перемещает схват робота в pos с ориентацией orn
Возвращает true, если перемещение удалось
Отменяет перемещение и возвращает false, если перемещение не
удалось"""
        # сохранение первоначального положения
        start_joints = [pb.getJointState(self.id, i)[0] for i in self._dofs]

        # значение для orn по умолчанию неизвестно
        if orn is None:
            IK = pb.calculateInverseKinematics(self.id, self.eff_id, pos,
                                               maxNumIterations=100,
                                               residualThreshold=self.__kin_eps)
        else:
            IK = pb.calculateInverseKinematics(self.id, self.eff_id, pos, orn,
                                               maxNumIterations=100,
                                               residualThreshold=self.__kin_eps)

        # задание полученного положения
        for i, joint in enumerate(self._dofs):
            pb.resetJointState(self.id, joint, IK[i])
        pb.stepSimulation()

        # проверка полученного решения
        new_pos = self.get_effector()
        if not (isclose(new_pos[0], pos[0], abs_tol=self.__kin_eps) and
                isclose(new_pos[1], pos[1], abs_tol=self.__kin_eps) and
                isclose(new_pos[2], pos[2], abs_tol=self.__kin_eps)):
            for i, joint in enumerate(self._dofs):
                pb.resetJointState(self.id, joint, start_joints[i])
            pb.stepSimulation()
            return False
            
        return True
    
    def check_collisions(self):
        """Проверяет объект робота на пересечения с объектами внешней
среды и самопересечения
Возвращает true, если существует хотя бы одно пересечение
Возвращает false, если пересечений нет"""

        # множество объектов, для которых необходима обработка
        # в узкой фазе
        obj_set = set()
        
        # широкая фаза
        for i in range(-1, pb.getNumJoints(self._id)):
            # координаты AABB
            box_min, box_max = pb.getAABB(self._id, i)
            
            # getOverlappingObjects возвращает кортежи,
            # первый элемент которых -- id объекта,
            # а второй -- id "звеньев" объекта
            # нужен только первый элемент
            ids = [obj[0]
                   for obj in pb.getOverlappingObjects(box_min, box_max)]
            obj_set |= set(ids)
            
        # узкая фаза
        contacts = []
        for o in obj_set:
            contacts += pb.getContactPoints(self._id, o)
        return len(contacts) > 0

    def get_effector(self):
        """Возвращает координаты центра тяжести рабочего органа"""
        return pb.getLinkState(self._id, self._eff_id)[0]
    
def getDOFIds(bId):
    """Получить сочленения со степенями свободы"""
    # пока что обрабатывает fixed, revolute и prismatic
    ret = list()
    for i in range(pb.getNumJoints(bId)):
        # в joint[2] лежит тип сочленения
        joint = pb.getJointInfo(bId, i)
        if joint[2] == pb.JOINT_REVOLUTE:
            ret.append(i)
        elif joint[2] == pb.JOINT_PRISMATIC:
            ret.append(i)

    return ret
