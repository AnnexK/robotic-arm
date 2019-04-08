import numpy as np
import scipy.linalg as la

from math import sin, cos, sqrt
from common_math import *

class Point:
    """Точка с однородными координатами"""
    
    def __init__(self, x=0.0, y=0.0, z=0.0, cartesian=True):
        """Сделать точку с декартовыми (по умолч.) координатами x, y, z"""
        self._data = np.array([x, y, z, 1 if cartesian else 0])

    def __str__(self):
        return '({}, {}, {}), w={}'.format(self.x, self.y, self.z, self.w)

    def __add__(self, other):
        """Сложение векторов и точек"""
        if self.w != 0 and other.w != 0: # две точки
            raise ValueError("Невозможно сложить операнды")
        else:
            # нормировать оба объекта
            self.norm() 
            other.norm()
            
            x = self.x + other.x
            y = self.y + other.y
            z = self.z + other.z
            # точка, если один из объектов не вектор
            isCart = self.w != 0 or other.w != 0
            return Point(x, y, z, isCart)

    def __sub__(self, other):
        if self.w == 0 and other.w != 0: # слева вектор, справа точка
            raise ValueError("Невозможно вычесть точку из вектора")
        else:
            self.norm()
            other.norm()
            
            x = self.x - other.x
            y = self.y - other.y
            z = self.z - other.z
            # точка, если слева точка, а справа вектор
            isCart = self.w != 0 and other.w == 0
            return Point(x, y, z, isCart)
        
    def __pow__(self, other):
        """Векторное произведение векторов"""
        if self.w != 0 or other.w != 0:
            raise ValueError("Операнды не являются векторами")
        else:
            x = self.y * other.z - self.z * other.y
            y = self.z * other.x - self.x * other.z
            z = self.x * other.y - self.y * other.x
            return Point(x, y, z, False)

    def __mul__(self, other):
        """Скалярное произведение векторов"""
        if self.w != 0 or other.w != 0:
            raise ValueError("Операнды не являются векторами")
        else:
            return self.x * other.x + self.y * other.y + self.z * other.z

    def __eq__(self, other):
        """Равенство двух точек/векторов"""
        return f_isclose(self.x, other.x) and f_isclose(self.y, other.y) and f_isclose(self.z, other.z) and self.w == other.w

    def __ne__(self, other):
        return not self.__eq__(other)
    
    @property
    def x(self):
        return self._data[0]

    @x.setter
    def x(self, value):
        self._data[0] = value

    @property
    def y(self):
        return self._data[1]

    @y.setter
    def y(self, value):
        self._data[1] = value

    @property
    def z(self):
        return self._data[2]

    @z.setter
    def z(self, value):
        self._data[2] = value

    @property
    def w(self):
        return self._data[3]
    
    def apply_transform(self, t_matrix):
        """Принимает матрицу numpy и умножает на нее точку"""
        self._data = t_matrix @ self._data # умножение матриц (@)

    def norm(self):
        if self.w != 0: # вектор всегда нормирован
            self.x = self.x / self.w
            self.y = self.y / self.w
            self.z = self.z / self.w
            self._data[3] = 1.0

    def length(self):
        if self.w != 0:
            raise ValueError("Объект не является вектором")
        else:
            return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)


class PrimitiveObject:
    """Базовый класс для всех сложных объектов"""
    def __init__(self, points):
        """Создать объект из набора точек"""
        self._points = np.array(points) # point - list из Point

    def __str__(self):
        ret = 'Points:\n' + '\n'.join(map(lambda p: p.__str__(), self._points))
        return ret

    def apply_transform(self, tmatrix):
        """Применить преобразование ко всем точкам объекта"""
        for p in self._points:
            p.apply_transform(tmatrix)


class Segment(PrimitiveObject):
    """Класс-отрезок

Содержимое _points:
0. Начальная точка
1. Конечная точка"""
    
    def __init__(self, x1=0.0, y1=0.0, z1=0.0, x2=0.0, y2=0.0, z2=0.0):
        """Создать отрезок с начальной точкой (x1, y1, z1) и конечной точкой
(x2, y2, z2)"""
        super().__init__([Point(x1, y1, z1), Point(x2, y2, z2)])

    def make_vector(self):
        """Получить из отрезка вектор"""
        return self._points[1] - self._points[0] # возвращает Point (w=0)

class Plane(PrimitiveObject):
    """Класс-плоскость
Содержит вектор нормали и точку в плоскости

Содержимое _points:
0. Вектор нормали
1. Точка, принадлежащая плоскости"""

    def __init__(self, a=0.0, b=0.0, c=0.0, d=0.0):
        """Создать плоскость с нормалью(nx, ny, nz) и точкой
(по умолчанию - плоскость xOy)"""
        if (a == 0.0 and b == 0.0 and c == 0.0):
            c = 1.0 # по умолчанию
        scale = -d / (a ** 2 + b ** 2 + c ** 2) # чтобы посчитать точку
        
        super().__init__([Point(a, b, c, False), Point(a * scale, b * scale, c * scale)])

    @property
    def norm(self):
        """Возвращает нормаль плоскости"""
        return self._points[0]
    
class Parallelepiped(PrimitiveObject):
    """Класс для описания прямоугольного параллелепипеда

Содержимое _points:
0-7. Вершины параллелепипеда"""
    def __init__(self, x=0.0, y=0.0, z=0.0, dx=1.0, dy=1.0, dz=1.0):
        """Создать прямоугольный параллелепипед с центром в x, y, z
и с размерами dx, dy, dz"""
        super().__init__(
        [Point(x+dx/2.0, y-dy/2.0, z-dz/2.0),
         Point(x-dx/2.0, y-dy/2.0, z-dz/2.0),
         Point(x-dx/2.0, y+dy/2.0, z-dz/2.0),
         Point(x+dx/2.0, y+dy/2.0, z-dz/2.0),
         Point(x+dx/2.0, y-dy/2.0, z+dz/2.0),
         Point(x-dx/2.0, y-dy/2.0, z+dz/2.0),
         Point(x-dx/2.0, y+dy/2.0, z+dz/2.0),
         Point(x+dx/2.0, y+dy/2.0, z+dz/2.0)])

    def make_segment(self, a, b):
        """Создать отрезок из точек с номерами a, b, если таковой есть"""
        segment_list = [[0,1],[1,2],[2,3],[3,0],
                        [4,5],[5,6],[6,7],[7,4],
                        [0,4],[1,5],[2,6],[3,7]]

        if [a,b] in segment_list or [b,a] in segment_list:
            x1 = self._points[a].x
            x2 = self._points[b].x
            y1 = self._points[a].y
            y2 = self._points[b].y
            z1 = self._points[a].z
            z2 = self._points[b].z
            return Segment(x1, y1, z1, x2, y2, z2)
        else:
            raise ValueError("Отрезка между точками a и b нет")


class RotationObject(PrimitiveObject):
    """Базовый класс для объектов вращения (цилиндры и конусы)

Содержимое _points:
0. Точка основания (x, y, z)
1. Вектор высоты
2. Вектор радиуса вращения"""
    def __init__(self, x=0.0, y=0.0, z=0.0, h=1.0, r=1.0):
        super().__init__(
            [Point(x, y, z),
             Point(0, 0, h, False),
             Point(r, 0, 0, False)])

    def __str__(self):
        ret = super().__str__()
        ret = ret + '\nHeight: {}'.format(self.height)
        ret = ret + '\nRadius: {}'.format(self.radius)
        return ret

    @property
    def height(self):
        return self._points[1].length()

    @property
    def radius(self):
        return self._points[2].length()

    @property
    def base_point(self):
        return self._points[0]

class Cylinder(RotationObject):
    """Класс для описания цилиндра

Содержимое _points : см. RotationObject"""
    def __init__(self, x=0.0, y=0.0, z=0.0, h=1.0, r=1.0):
        super().__init__(x, y, z, h, r)


class Cone(RotationObject):
    """Класс для описания конуса (в т.ч. усеченного)

Содержимое _points: 
0-2. см. RotationObject
3. Вектор высоты отсечения"""
    def __init__(self, x=0.0, y=0.0, z=0.0, h=1.0, hr=None, r=1.0):
        if hr is None: # неусеченный конус
            hr = h
        super().__init__(x, y, z, h, r)
        self._points = np.append(self._points, Point(0, 0, hr, False)) # добавить вектор высоты отсечения

    def __str__(self):
        ret = super().__str__()
        ret = ret + '\nSecond height: {}'.format(self._points[3].length())
        return ret

    @property
    def second_height(self):
        return self._points[3].length()

    def make_second_radius(self):
        """Получить вектор радиуса отсечения"""
        scale = (self.height - self.second_height) / self.height
        x = self._points[2].x * scale
        y = self._points[2].y * scale
        z = self._points[2].z * scale
        return Point(x, y, z, False)


def TSR(dx=0.0, dy=0.0, dz=0.0, p=0.0, t=0.0, ps=0.0, sx=1.0, sy=None, sz=None):
    """Построение матрицы преобразований

    dx, dy, dz - коэффициенты переноса,
    p - угол поворота вокруг Oz,
    t - угол поворота вокруг Oy,
    ps - угол поворота вокруг Ox,

    sx, sy, sz - коэффициенты масштабирования,
    если предоставлен только аргумент sx, то остальные считаются равным ему"""
    if (sy is None and sz is None): # один скаляр
        sy = sx
        sz = sx
    else:
        if (sy is None):
            sy = 1.0
        if (sz is None):
            sz = 1.0            
    return np.array([
        [cos(p)*sx,          (cos(p)*sin(t)*sin(ps)-sin(p)*cos(ps))*sx, (cos(p)*sin(t)*cos(ps)+sin(t)*cos(ps))*sx, dx],
        [(sin(p)*cos(t))*sy, (sin(p)*sin(t)*sin(ps)+cos(p)*cos(ps))*sy, (sin(p)*sin(t)*cos(ps)-cos(t)*sin(ps))*sy, dy],
        [(-sin(t))*sz,       (cos(t)*sin(ps))*sz,                       (cos(t)*cos(ps))*sz,                       dz],
        [0,                  0,                                         0,                                          1]])
