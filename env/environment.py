import pybullet as pb


class Environment:
    """Обертка над объектами pybullet, содержащая информацию
об объектах внешней среды и предназначенная для хранения информации
и удобного освобождения ресурсов"""
    def __init__(self, filename=None):
        """Параметры:
filename -- имя SDF-файла (абсолютный путь)
при отсутствии параметра создается пустая внешняя среда"""
        if filename is None:
            self._ids = list()  # пустой
        else:
            try:
                self._ids = pb.loadSDF(filename)
            except pb.error:
                raise ValueError('failed to read SDF file')
        for body_id in self._ids:
            pb.resetBaseVelocity(body_id, (0, 0, 0), (0, 0, 0))

    def __getitem__(self, i):
        """Возвращает идентификатор PB i-го объекта"""
        return self._ids[i]

    def __del__(self):
        """Предназначено для освобождения ресурсов"""
        for i in self._ids:
            pb.removeBody(i)
