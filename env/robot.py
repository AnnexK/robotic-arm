import pybullet as pb
from math import inf, isclose
from logger import log
from typing import List, Tuple, Optional, Set, Any, Callable
from .types import State, Vector3
from .taskdata import TaskData


Quaternion = Tuple[float, float, float, float]


class Robot:
    """Обертка над объектом pybullet, содержащая информацию
об объекте робота и позволяющая производить операции перемещения
рабочего органа, получения информации о положении рабочего
органа и проверки на столкновения"""
    def _get_dof_ids(self) -> List[int]:
        """Получить сочленения со степенями свободы"""
        # пока что обрабатывает fixed, revolute и prismatic
        ret: List[int] = list()
        i: int
        for i in range(pb.getNumJoints(self.id, #type: ignore
                                       physicsClientId=self.s)):
            # в joint[2] лежит тип сочленения
            joint: Any = pb.getJointInfo(self.id, i, #type: ignore
                                         physicsClientId=self.s)
            # также обрабатывает continuous сочленения
            if joint[2] == pb.JOINT_REVOLUTE: #type: ignore
                ret.append(i)
            elif joint[2] == pb.JOINT_PRISMATIC: #type: ignore
                ret.append(i)
        return ret

    def _get_limits(self) -> Tuple[List[float], List[float]]:
        lower: List[float] = []
        upper: List[float] = []
        for i in range(pb.getNumJoints(self.id, #type: ignore
                                       physicsClientId=self.s)):
            joint: Any = pb.getJointInfo(self.id, i, #type: ignore
                                         physicsClientId=self.s)
            if joint[2] != pb.JOINT_FIXED: #type: ignore
                if joint[8] > joint[9]:
                    lower.append(-inf)
                    upper.append(inf)
                else:
                    lower.append(joint[8])  # нижний предел
                    upper.append(joint[9])  # верхний предел
        return (lower, upper)

    def __init__(self, server: int, td: TaskData):
        # читаем urdf файл
        try:
            q_orn: Quaternion = pb.getQuaternionFromEuler(td.orn) #type: ignore
            self._id: int = pb.loadURDF(td.urdf, #type: ignore
                                        basePosition=td.pos,
                                        baseOrientation=q_orn,
                                        flags=pb.URDF_USE_SELF_COLLISION, #type: ignore
                                        useFixedBase=td.fixed,
                                        physicsClientId=server)
        except pb.error as err: #type: ignore
            raise ValueError('failed to read urdf file') from err

        self.s = server

        self._kin_eps: float = td.eps

        f: Callable[[Any], bool] = lambda j: j[12].decode() == td.effector
        joints: List[Any] = [pb.getJointInfo(self._id, i, #type: ignore
                             physicsClientId=self.s)
                             for i in range(pb.getNumJoints(self._id, #type: ignore
                                                            physicsClientId=self.s))]
        try:
            # достаем индекс звена-схвата
            self._eff_id: int = filter(
                f,
                joints
            ).__next__()[0]
        except StopIteration:
            raise ValueError(
                'effector with name {} not found'.format(td.effector))

        # получаем список индексов звеньев со степенями свободы
        self._dofs = self._get_dof_ids()
        self._lower, self._upper = self._get_limits()
        self.ranges = [u - l for u, l in zip(self._upper, self._lower)]
        self._damping = [0.01 for _ in self._dofs]

        if td.init_state is not None:
            self.state = td.init_state
        self.pose = [(low+up)/2 if low != -inf
                     else 0.0
                     for low, up in zip(self._lower, self._upper)]

    def __del__(self):
        """Предназначено для освобождения ресурсов pybullet"""
        # удалить объект из pb при уничтожении Robot
        pb.removeBody(self._id, #type: ignore
                      physicsClientId=self.s)

    # id для доступа средствами pb
    @property
    def id(self) -> int:
        return self._id

    # индекс рабочего органа
    @property
    def eff_id(self) -> int:
        return self._eff_id

    @property
    def kin_eps(self) -> float:
        return self._kin_eps

    @property
    def state(self) -> State:
        return tuple( 
            pb.getJointState(self.id, i, physicsClientId=self.s)[0] #type: ignore
            for i in self._dofs
        )

    @state.setter
    def state(self, val: State):
        if len(val) != len(self._dofs):
            raise ValueError('Wrong number of DoFs')

        for lower, v, upper in zip(self._lower, val, self._upper):
            # нет ограничений на значение
            if not (lower <= v <= upper):
                raise ValueError('Values not in bounds')

        for i, joint in enumerate(self._dofs):
            pb.resetJointState(self.id, joint, val[i], #type: ignore
                               targetVelocity=0.0,
                               physicsClientId=self.s)
        pb.stepSimulation(physicsClientId=self.s) #type: ignore

    @property
    def lower(self) -> List[float]:
        return self._lower

    @property
    def upper(self) -> List[float]:
        return self._upper

    def move_to(self, pos: Vector3, orn: Optional[Vector3] = None):
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
            tmp: List[float] = pb.calculateInverseKinematics( #type: ignore
                self.id,
                self.eff_id, pos,
                maxNumIterations=iters,
                lowerLimits=self._lower,
                upperLimits=self._upper,
                jointRanges=self.ranges,
                restPoses=self.pose,
                jointDamping=self._damping,
                residualThreshold=accuracy,
                physicsClientId=self.s
            )
        else:
            tmp: List[float] = pb.calculateInverseKinematics( #type: ignore
                self.id,
                self.eff_id, pos, orn,
                maxNumIterations=iters,
                lowerLimits=self._lower,
                upperLimits=self._upper,
                jointRanges=self.ranges,
                restPoses=self.pose,
                jointDamping=self._damping,
                residualThreshold=accuracy,
                physicsClientId=self.s
            )
        IK: State = tuple(tmp)
        # log()['IK'].log(IK)
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

    def check_collisions(self) -> bool:
        """Проверяет объект робота на пересечения с объектами внешней
среды и самопересечения
Возвращает true, если существует хотя бы одно пересечение
Возвращает false, если пересечений нет"""

        # множество объектов, для которых необходима обработка
        # в узкой фазе
        obj_set: Set[int] = set()

        # широкая фаза
        for i in range(-1, pb.getNumJoints(self._id, #type: ignore
                                           physicsClientId=self.s)):
            # координаты AABB
            box_min, box_max = pb.getAABB(self._id, i, #type: ignore
                                          physicsClientId=self.s)

            # getOverlappingObjects возвращает кортежи,
            # первый элемент которых -- id объекта,
            # а второй -- id "звеньев" объекта
            # нужен только первый элемент
            ids: List[int] = [
                obj[0]
                for obj in #type: ignore
                pb.getOverlappingObjects(box_min, box_max, #type: ignore
                                         physicsClientId=self.s)
            ]
            obj_set |= set(ids)

        # узкая фаза
        contacts: List[Any] = []
        for o in obj_set:
            contacts += pb.getContactPoints(self._id, o, #type: ignore
                                            physicsClientId=self.s)

        return (not (not contacts)) and any(c[8] < -0.002 for c in contacts)

    def get_effector(self) -> Vector3:
        """Возвращает координаты центра тяжести рабочего органа"""
        return pb.getLinkState(self._id, self._eff_id, #type: ignore
                               physicsClientId=self.s)[0]
