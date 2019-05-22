import pybullet as pb
import json
import os

def robot_json_parse(dct):
    """Добавляет к прочитанному из json словарю значения по умолчанию,
если они не были предоставлены"""
    if not 'pos' in dct:
        dct['pos'] = (.0,.0,.0)
    if not 'orn' in dct:
        dct['orn'] = (0.0, 0.0, 0.0) # rpy
    return dct

class Robot:
    def __init__(self, filename):
        # читаем json
        with open(filename, 'r') as fp:
            data = json.load(fp, object_hook=robot_json_parse)

        # получаем полный путь до urdf файла
        path_list = filename.split(os.sep)[:-1:]
        urdf_filename = os.path.join(os.sep.join(path_list),
                                     data['urdf_name'])
        # читаем urdf файл
        self._id = pb.loadURDF(urdf_filename,
                               basePosition=data['pos'],
                               baseOrientation=pb.getQuaternionFromEuler(data['orn']),
                               flags=pb.URDF_USE_SELF_COLLISION)

        # достаем индекс звена-схвата
        self._eff_id = filter(
            lambda j : j[12].decode() == data['effector_name'],
            [pb.getJointInfo(self._id,i)
             for i in range(pb.getNumJoints(self._id))]
        ).__next__()[0]

        # получаем список индексов звеньев со степенями свободы
        self._dofs = getDOFIds(self._id)
        
    def __del__(self):
        """Предназначено для освобождения ресурсов"""
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
        """Перемещает схват робота в pos с ориентацией orn"""
        if orn is None:
            IK = pb.calculateInverseKinematics(self.id, self.eff_id, pos)
        else:
            IK = pb.calculateInverseKinematics(self.id, self.eff_id, pos, orn)
        for i, joint in enumerate(self._dofs):
            pb.resetJointState(self.id, joint, IK[i])

    def check_collisions(self):
        obj_set = set()
        for i in range(-1, pb.getNumJoints(self.id)):
            box_min, box_max = pb.getAABB(self.id, i)
            ids = [obj[0]
                   for obj in pb.getOverlappingObjects(box_min, box_max)]
            obj_set |= set(ids)
        contacts = [pb.getContactPoints(self.id, i) for i in obj_set]
        return len(contacts) == 0
    
def getDOFIds(bId):
    """Получить сочленения со степенями свободы"""
    # пока что обрабатывает fixed, revolute и prismatic
    ret = list()
    for i in range(pb.getNumJoints(bId)):
        joint = pb.getJointInfo(bId, i)
        if joint[2] == pb.JOINT_REVOLUTE:
            ret.append(i)
        elif joint[2] == pb.JOINT_PRISMATIC:
            ret.append(i)

    return ret
