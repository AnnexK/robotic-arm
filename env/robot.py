from numpy import asarray
from numpy.random import random

import pybullet as pb
from math import inf, isclose
from logger import log


class Robot:
    """Обертка над объектом pybullet, содержащая информацию
об объекте робота и позволяющая производить операции перемещения
рабочего органа, получения информации о положении рабочего
органа и проверки на столкновения"""
    def _get_dof_ids(self):
        """Получить сочленения со степенями свободы"""
        # пока что обрабатывает fixed, revolute и prismatic
        ret = list()
        for i in range(pb.getNumJoints(self.id,
                                       physicsClientId=self.s)):
            # в joint[2] лежит тип сочленения
            joint = pb.getJointInfo(self.id, i,
                                    physicsClientId=self.s)
            # также обрабатывает continuous сочленения
            if joint[2] == pb.JOINT_REVOLUTE:
                ret.append(i)
            elif joint[2] == pb.JOINT_PRISMATIC:
                ret.append(i)
        return ret

    def _get_limits(self):
        lower, upper = [], []
        for i in range(pb.getNumJoints(self.id,
                                       physicsClientId=self.s)):
            joint = pb.getJointInfo(self.id, i,
                                    physicsClientId=self.s)
            if joint[2] != pb.JOINT_FIXED:
                if joint[8] > joint[9]:
                    lower.append(-inf)
                    upper.append(inf)
                else:
                    lower.append(joint[8])  # нижний предел
                    upper.append(joint[9])  # верхний предел
        return lower, upper

    def __init__(self, server=0, **kwargs):
        """Параметры:
filename -- имя URDF-файла (абсолютный путь)
eff_name -- имя звена-рабочего органа
pos -- координаты местоположения базового звена
orn -- ориентация базового звена (кватернион)
fixed -- флаг фиксирования положения базы (0/1)
kin_eps -- значение погрешности для решения ОКЗ"""
        if 'pos' not in kwargs:
            kwargs['pos'] = (0, 0, 0)
        if 'orn' not in kwargs:
            kwargs['orn'] = (0, 0, 0)
        if 'fixed' not in kwargs:
            kwargs['fixed'] = True
        if 'kin_eps' not in kwargs:
            kwargs['kin_eps'] = 1e-2

        keys = ['filename',
                'eff_name',
                'pos',
                'orn',
                'fixed',
                'kin_eps']

        (filename,
         eff_name,
         pos,
         orn,
         fixed,
         kin_eps) = tuple(kwargs[k] for k in keys)

        # читаем urdf файл
        try:
            q_orn = pb.getQuaternionFromEuler(orn)
            self._id = pb.loadURDF(filename,
                                   basePosition=pos,
                                   baseOrientation=q_orn,
                                   flags=pb.URDF_USE_SELF_COLLISION,
                                   useFixedBase=fixed,
                                   physicsClientId=server)
        except pb.error as err:
            raise ValueError('failed to read urdf file') from err

        self.s = server

        self._kin_eps = kin_eps

        try:
            # достаем индекс звена-схвата
            self._eff_id = filter(
                lambda j: j[12].decode() == eff_name,
                [pb.getJointInfo(self._id, i,
                                 physicsClientId=self.s)
                 for i in range(pb.getNumJoints(self._id,
                                                physicsClientId=self.s))]
            ).__next__()[0]
        except StopIteration:
            raise ValueError(
                'effector with name {} not found'.format(eff_name))

        # получаем список индексов звеньев со степенями свободы
        self._dofs = self._get_dof_ids()
        self._lower, self._upper = self._get_limits()
        self.ranges = [u - l for u, l in zip(self._upper, self._lower)]
        self._damping = [0.01 for i in self._dofs]

        self.pose = [(l+u)/2 if l != -inf
                     else 0.0
                     for l, u in zip(self._lower, self._upper)]

    def __del__(self):
        """Предназначено для освобождения ресурсов pybullet"""
        # удалить объект из pb при уничтожении Robot
        pb.removeBody(self._id,
                      physicsClientId=self.s)
            
    # id для доступа средствами pb
    @property
    def id(self):
        return self._id

    # индекс рабочего органа
    @property
    def eff_id(self):
        return self._eff_id

    @property
    def kin_eps(self):
        return self._kin_eps

    @property
    def state(self):
        return asarray([pb.getJointState(self.id, i,
                                         physicsClientId=self.s)[0]
                        for i in self._dofs])

    @state.setter
    def state(self, val):
        if len(val) != len(self._dofs):
            raise ValueError('Wrong number of DoFs')

        for lower, v, upper in zip(self._lower, val, self._upper):
            # нет ограничений на значение
            if lower > upper:
                continue
            elif not (lower <= v <= upper):
                raise ValueError('Values not in bounds')

        for i, joint in enumerate(self._dofs):
            pb.resetJointState(self.id, joint, val[i],
                               physicsClientId=self.s)
        pb.stepSimulation(physicsClientId=self.s)

    def move_to(self, pos, orn=None):
        """Перемещает схват робота в pos с ориентацией orn
Возвращает true, если перемещение удалось
Отменяет перемещение и возвращает false, если перемещение не
удалось"""
        # сохранение первоначального положения
        start_joints = self.state

        accuracy = self.kin_eps / 2
        iters = round(1/accuracy)

        # значение для orn по умолчанию неизвестно
        if orn is None:
            IK = pb.calculateInverseKinematics(self.id, self.eff_id, pos,
                                               maxNumIterations=iters,
                                               lowerLimits=self._lower,
                                               upperLimits=self._upper,
                                               jointRanges=self.ranges,
                                               restPoses=self.pose,
                                               jointDamping=self._damping,
                                               residualThreshold=accuracy,
                                               physicsClientId=self.s)
        else:
            IK = pb.calculateInverseKinematics(self.id, self.eff_id, pos, orn,
                                               lowerLimits=self._lower,
                                               upperLimits=self._upper,
                                               jointRanges=self.ranges,
                                               restPoses=self.pose,
                                               maxNumIterations=iters,
                                               jointDamping=self._damping,
                                               residualThreshold=accuracy,
                                               physicsClientId=self.s)

        log()['IK'].log(IK)
        # задание полученного положения
        try:
            self.state = IK
        except ValueError:
            log()['PYBULLET'].log('unable to set state: vals out of bounds')
            self.state = start_joints
            return False
        # проверка полученного решения
        new_pos = self.get_effector()
        if not (isclose(new_pos[0], pos[0], abs_tol=accuracy) and
                isclose(new_pos[1], pos[1], abs_tol=accuracy) and
                isclose(new_pos[2], pos[2], abs_tol=accuracy)):
            self.state = start_joints
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
        for i in range(-1, pb.getNumJoints(self._id,
                                           physicsClientId=self.s)):
            # координаты AABB
            box_min, box_max = pb.getAABB(self._id, i,
                                          physicsClientId=self.s)

            # getOverlappingObjects возвращает кортежи,
            # первый элемент которых -- id объекта,
            # а второй -- id "звеньев" объекта
            # нужен только первый элемент
            ids = [obj[0]
                   for obj in
                   pb.getOverlappingObjects(box_min, box_max,
                                            physicsClientId=self.s)]
            obj_set |= set(ids)

        # узкая фаза
        contacts = []
        for o in obj_set:
            contacts += pb.getContactPoints(self._id, o,
                                            physicsClientId=self.s)
        return len(contacts) > 0

    def get_effector(self):
        """Возвращает координаты центра тяжести рабочего органа"""
        return pb.getLinkState(self._id, self._eff_id,
                               physicsClientId=self.s)[0]
