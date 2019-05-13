from math import sin, cos, pi, atan2, acos, sqrt
from functools import reduce
import geometry as geom
from common_math import isclose_wrap

class Edge:
    def __init__(self, length, angle=0.0, angle_l=None, angle_r=None):
        if angle_l == None:
            angle_l = -pi
        if angle_r == None:
            angle_r = pi
            
        if angle_l < -pi or angle_r > pi or angle < angle_l or angle > angle_r or angle_l > angle_r:
            raise ValueError('Неверное значение угла поворота')
            
        self.len = length
        self.angle = angle
        self.angle_l = angle_l
        self.angle_r = angle_r
    
    def __str__(self):
        return '<L={}, phi=[{}; {} ({})]>'.format(self.len, self.angle_l, self.angle_r, self.angle)
    
    def rotate(self, angle):
        l_eq = isclose_wrap(self.angle_l, self.angle+angle)
        r_eq = isclose_wrap(self.angle_r, self.angle+angle)
        
        if self.angle_l < self.angle + angle < self.angle_r or l_eq or r_eq:
            self.angle += angle
        else:
            raise ValueError('Невозможно произвести наклон')

        
class RoboticArm:
    """Класс, моделирующий поведение робота-манипулятора с схватом.
    
    Положение манипулятора в пространстве определяется начальной
    точкой с координатами x, y, z, углом между плоскостью и осью OX
    angle и набором последовательно соединенных звеньев, имеющих длину L
    и угол между соседними звеньями angle."""
    
    def __init__(self, x=0.0, y=0.0, z=0.0, angle=0.0, base_len=1.0):
        try:
            self.origin = geom.Point(x, y, z)
            self.edges = [Edge(base_len)] # база как звено
            self.angle = angle
        except ValueError as E:
            print(E)

    def __str__(self):
        ret = 'Edges:\n' + '\n'.join(map(lambda e: e.__str__(), self.edges))
        ret = ret + '\nVertices:\n' + '\n'.join(map(lambda v: v.__str__(), self.calculate_vertices()))
        ret = ret + '\nCurrent angle: {}'.format(self.angle)
        return ret
    
    
    def append_edge(self, L, angle=0.0, al=None, ar=None):
        """Добавляет звено"""
        self.edges.append(Edge(L, angle, al, ar))

    def get_angles(self):
        """Возвращает список углов"""
        return [self.angle] + [e.angle for e in self.edges[1::]]
    
    def calculate_vertices(self):
        """Возвращает положение сочленений звеньев"""
        ret = [self.origin]
        angle_z = 0.0

        # угол поворота базы для всех звеньев одинаков
        cost = cos(self.angle)
        sint = sin(self.angle)
        
        for edge in self.edges:
            angle_z += edge.angle

            L = edge.len
            
            vec = geom.Point(L * cost * sin(angle_z),
                             L * sint * sin(angle_z),
                             L * cos(angle_z),
                             False)
            ret.append(ret[-1] + vec)
        return ret

    """Возвращает положение схвата (последнее звено)"""
    def calculate_grip(self):
        return self.calculate_vertices()[-1]

    def rotate_edge(self, nedge, angle):
        try:
            self.edges[nedge].rotate(angle)
        except ValueError as E:
            print(E)
            print('Номер ребра: {}'.format(nedge))

    def rotate(self, angle):
        self.angle += angle
        if -pi > self.angle or self.angle > pi: # переписать
            while self.angle < -pi:
                self.angle += 2 * pi
            while self.angle > pi:
                self.angle -= 2 * pi                

    def move(self, dx, dy, dz):
        """Параллельный перенос модели"""
        self.origin = self.origin + geom.Point(dx,
                                               dy,
                                               dz, False)

    def grip_move(self, angles):
        """Перемещение схвата на заданные углы
angles[0] - угол поворота базы
angles[1..n] - углы поворота соотв звеньев"""
        if angles is None:
            raise ValueError('Перемещение схвата в точку невозможно')

        if len(angles) != len(self.edges):
            raise ValueError('Несоответстве количества углов')
        
        self.rotate(angles[0])

        for nedge in range(1, len(self.edges)):
            self.rotate_edge(nedge, angles[nedge])


def grip_calculate_angles(R, x, y, z):
    if len(R.edges) == 4:
        angles = grip_calculate_angles_geom(R, x, y, z)
        if angles is None:
            return None
        else:
            angles[0][0] -= R.angle
            for nedge, edge in enumerate(R.edges[1::]):
                angles[0][nedge+1] -= edge.angle
            return angles[0] # пока одно решение
    else:
        return None # более универсальный метод
    
def grip_calculate_angles_geom(R, x, y, z):
    """Геометрическое решение ОКЗ для двухзвенных манипуляторов"""
    if len(R.edges) != 4: # база, два ребра, схват
        raise ValueError('Неподходящая модель робота')
    
    # перенос координат
    dx = x - R.origin.x
    dy = y - R.origin.y
    dz = z - R.origin.z
    
    base_len = R.edges[0].len # длина базы
    e1_len = R.edges[1].len # длина первого ребра
    e2_len = R.edges[2].len # длина второго ребра
    grip_len = R.edges[3].len # длина ребра схвата

    # начальная точка (без ребра-базы)
    start_z = dz - base_len + grip_len
    # первый угол - угол поворота базы
    ret = ([atan2(dy, dx)], [atan2(dy, dx)]) 

    # длина главной оси
    d = sqrt(dx ** 2 + dy ** 2)
    # длина пути от первого сочленения до необходимой точки
    s = sqrt(start_z ** 2 + d ** 2)
    # s == 0 -> точка назначения внутри базы
    if isclose_wrap(s, 0.0):
        return None
    
    total_length = reduce((lambda x, y : x.len + y.len), R.edges[1:3:])
    if total_length < s: # никак не дотянуться
        return None
        
    alpha = atan2(start_z, d)
    beta = acos((s ** 2 + e1_len ** 2 - e2_len ** 2) / (2 * s * e1_len))
        
    ret[0].append(pi/2 - (alpha + beta)) # одно решение
    ret[1].append(pi/2 - (alpha - beta)) # второе решение        

    theta_2 = acos((s ** 2 - e1_len ** 2 - e2_len ** 2) / (2 * e1_len * e2_len))
    ret[0].append(theta_2)
    ret[1].append(-theta_2)
    
    # углы схвата
    ret[0].append(pi - ret[0][1] - ret[0][2])
    ret[1].append(pi - ret[1][1] - ret[1][2])
    return ret

def make_robot(Lb=1.0, L1=3.0, L2=3.0, Lg=0.25):
    """Создает модель двухзвенного робота с заданными длинами базы, звеньев и схвата
в точке (0;0;0) с углом поворота 0 рад."""
    R = RoboticArm(base_len=Lb)
    R.append_edge(L=L1)
    R.append_edge(L=L2, angle=pi/2)
    R.append_edge(L=Lg, angle=pi/2)
    return R
