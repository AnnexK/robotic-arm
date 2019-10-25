import pybullet as pb
from math import isclose
# import json


class Robot:
    """Обертка над объектом pybullet, содержащая информацию
об объекте робота и позволяющая производить операции перемещения
рабочего органа, получения информации о положении рабочего
органа и проверки на столкновения"""
    def __init__(self, filename, eff_name,
                 pos=(0, 0, 0),
                 orn=(0, 0, 0),
                 fixed=True,
                 kin_eps=1e-2):
        """Параметры:
filename -- имя URDF-файла (абсолютный путь)
eff_name -- имя звена-рабочего органа
pos -- координаты местоположения базового звена
orn -- ориентация базового звена (кватернион)
fixed -- флаг фиксирования положения базы (0/1)
kin_eps -- значение погрешности для решения ОКЗ"""
        # читаем urdf файл
        try:
            self._id = pb.loadURDF(filename,
                                   basePosition=pos,
                                   baseOrientation=pb.getQuaternionFromEuler(orn),
                                   flags=pb.URDF_USE_SELF_COLLISION,
                                   useFixedBase=fixed)
        except pb.error as err:
            raise ValueError('failed to read urdf file') from err

        self._kin_eps = kin_eps

        try:
            # достаем индекс звена-схвата
            self._eff_id = filter(
                lambda j: j[12].decode() == eff_name,
                [pb.getJointInfo(self._id, i)
                 for i in range(pb.getNumJoints(self._id))]
            ).__next__()[0]
        except StopIteration:
            raise ValueError(
                'effector with name {} not found'.format(eff_name))

        # получаем список индексов звеньев со степенями свободы
        self._dofs = getDOFIds(self._id)
        self._lower, self._upper = get_limits(self.id)

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

    @property
    def kin_eps(self):
        return self._kin_eps

    @property
    def state(self):
        return [pb.getJointState(self.id, i)[0] for i in self._dofs]

    @state.setter
    def state(self, val):
        if len(val) != len(self._dofs):
            raise ValueError('Wrong number of DoFs')

        for i, joint in enumerate(self._dofs):
            pb.resetJointState(self.id, joint, val[i])
        pb.stepSimulation()

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
                                               residualThreshold=accuracy)
        else:
            IK = pb.calculateInverseKinematics(self.id, self.eff_id, pos, orn,
                                               maxNumIterations=iters,
                                               residualThreshold=accuracy)

        # задание полученного положения
        self.state = IK
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
        for i in range(-1, pb.getNumJoints(self._id)):
            # координаты AABB
            box_min, box_max = pb.getAABB(self._id, i)

            # getOverlappingObjects возвращает кортежи,
            # первый элемент которых -- id объекта,
            # а второй -- id "звеньев" объекта
            # нужен только первый элемент
            ids = [obj[0]
                   for obj in
                   pb.getOverlappingObjects(box_min, box_max)]
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


def get_limits(bId):
    lower, upper = [], []
    for i in range(pb.getNumJoints(bId)):
        joint = pb.getJointInfo(bId, i)
        if joint[2] != pb.JOINT_FIXED:
            lower.append(joint[8])  # нижний предел
            upper.append(joint[9])  # верхний предел

    return lower, upper
