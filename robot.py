from math import sin, cos, pi

class Vertex:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return "({}; {}; {})".format(self.x, self.y, self.z)
        
class Edge:
    def __init__(self, length, len_l=None, len_r=None, angle=0.0, angle_l=None, angle_r=None):
        if len_l == None:
            len_l = length
        if len_r == None:
            len_r = length
            
        if len_l > len_r or length < len_l or length > len_r or len_l <= 0:
            raise ValueError('Неверное значение длины или границ длины')

        if angle_l == None:
            angle_l = angle
        if angle_r == None:
            angle_r = angle
            
        if angle_l < -pi or angle_r > pi or angle < angle_l or angle > angle_r or angle_l > angle_r:
            raise ValueError('Неверное значение угла поворота')
            
        self.len = length
        self.len_l = len_l
        self.len_r = len_r
        self.angle = angle
        self.angle_l = angle_l
        self.angle_r = angle_r
    
    def __str__(self):
        return '<L=[{}; {} ({})], phi=[{}; {} ({})]>'.format(self.len_l, self.len_r, self.len, self.angle_l, self.angle_r, self.angle)
    
    def rotate(self, angle):
        if self.angle_l <= self.angle + angle <= self.angle_r:
            self.angle += angle
        else:
            raise ValueError('Невозможно произвести наклон')

    def expand(self, l):
        if self.len_l <= self.len + l <= self.len_r:
            self.len += l
        else:
            raise ValueError('Невозможно произвести изменение длины')

        
class RoboticArm:
    """Класс, моделирующий поведение робота-манипулятора с схватом.
    
    Положение манипулятора в пространстве определяется начальной
    точкой с координатами x, y, z, углом между плоскостью и осью OX
    angle и набором последовательно соединенных звеньев, имеющих длину L
    и угол между соседними ребрами angle."""
    
    def __init__(self, x=0.0, y=0.0, z=0.0, angle=0.0, base_len=1.0):
        try:
            self.origin = Vertex(x, y, z)
            self.edges = [Edge(base_len)]
            self.angle = angle
        except ValueError as E:
            print(E)

    def __str__(self):
        ret = 'Edges:\n' + '\n'.join(list(map(lambda e: e.__str__(), self.edges)))
        ret = ret + '\nVertices:\n' + '\n'.join(list(map(lambda v: v.__str__(), self.calculate_vertices())))
        ret = ret + '\nCurrent angle: {}'.format(self.angle)
        return ret
    
    """Добавляет звено"""
    def append_edge(self, L, ll=None, lr=None, angle=0.0, al=None, ar=None):
        self.edges.append(Edge(L, ll, lr, angle, al, ar))

    """Возвращает положение сочленений звеньев"""
    def calculate_vertices(self):
        ret = [self.origin]
        angle_z = 0.0
        
        cost = cos(self.angle)
        sint = sin(self.angle)
        
        for edge in self.edges:
            angle_z += edge.angle
            
            new_x = ret[-1].x + edge.len*sin(angle_z)*cost
            new_y = ret[-1].y + edge.len*sin(angle_z)*sint
            new_z = ret[-1].z + edge.len*cos(angle_z)
            
            ret.append(Vertex(new_x, new_y, new_z))
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
            
    def expand_edge(self, nedge, length):
        try:
            self.edges[nedge].expand(length)
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

    """Параллельный перенос модели"""
    def move(self, dx, dy, dz):
        self.origin.x += dx
        self.origin.y += dy
        self.origin.z += dz
    
if __name__ == "__main__":
    r = RoboticArm()
    r.append_edge(L=2, angle=pi/4)
    r.append_edge(L=2, angle=pi/2)
    r.append_edge(L=3, ll=1, al=0.0, ar=pi/2)
    
    print(r)
    r.rotate_edge(1, pi)
    
    print(r)

    r.rotate(pi/2)
    print(r)
