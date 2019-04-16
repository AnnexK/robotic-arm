from math import sin, cos, pi, atan2, acos, sqrt
from functools import reduce
import geometry as geom

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
        if self.angle_l <= self.angle + angle <= self.angle_r:
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
    
    
    def append_edge(self, L, ll=None, lr=None, angle=0.0, al=None, ar=None):
        """Добавляет звено"""
        self.edges.append(Edge(L, ll, lr, angle, al, ar))

    
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
            
            vec = geom.Point(L * cost * sin(angle_z), L * sint * sin(angle_z), L * cos(angle_z), False)
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
        if not -pi <= self.angle <= pi: # переписать
            while self.angle < -pi:
                self.angle += 2 * pi
            while self.angle > pi:
                self.angle -= 2 * pi                

    def move(self, dx, dy, dz):
        """Параллельный перенос модели"""
        self.origin = self.origin + geom.Point(dx, dy, dz, False)

    def grip_move(self, x, y, z):
        """Перемещение схвата в точку с координатами x, y, z"""
        angles = None
        
        if len(self.edges) == 3:
            angles = self.grip_move_geom(x, y, z)
        else:
            pass # более универсальный метод

        if angles is None:
            raise ValueError('Перемещение схвата в точку невозможно')
        
        self.rotate(angles[0][0] - self.angle)

        for nedge, edge in enumerate(self.edges[1::]):
            self.rotate_edge(nedge+1, angles[0][nedge+1] - edge.angle)

    def grip_move_geom(self, x, y, z):
        """Геометрическое решение ОКЗ для двухзвенных манипуляторов"""
        if len(self.edges) != 3:
            raise ValueError('Геометрический метод работает только для двухзвенных манипуляторов')

        start_z = z - self.edges[0].len # начальная точка (без ребра-базы)
        e1_len = self.edges[1].len
        e2_len = self.edges[2].len
        
        ret = ([atan2(y, x)], [atan2(y, x)]) # первый угол - угол поворота базы

        d = sqrt(x ** 2 + y ** 2) # длина главной оси
        s = sqrt(start_z ** 2 + d ** 2) # длина пути от первого сочленения до необходимой точки

        total_length = reduce((lambda x, y : x.len + y.len), self.edges[1::])
        if total_length < s: # никак не дотянуться
            return None
        
        alpha = atan2(start_z, d)
        beta = acos((s ** 2 + e1_len ** 2 - e2_len ** 2) / (2 * s * e1_len))

        ret[0].append(pi/2 - (alpha + beta)) # одно решение
        ret[1].append(pi/2 - (alpha - beta)) # второе решение        

        theta_2 = acos((s ** 2 - e1_len ** 2 - e2_len ** 2) / (2 * e1_len * e2_len))
        ret[0].append(theta_2)
        ret[1].append(-theta_2)

        return ret
