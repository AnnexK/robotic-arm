from math import sin, cos, pi

class Vertex:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return "({}; {}; {})".format(self.x, self.y, self.z)
        
class Edge:
    def __init__(self, length, phi, theta):
        self.L = length
        self.phi = phi
        self.theta = theta

    def __str__(self):
        return "<L={}, phi={}, theta={}>".format(self.L, self.phi, self.theta)
    
    def rotate_z(self, angle):
        self.phi += angle

    def rotate_xy(self, angle):
        self.theta += angle

        
class RoboticArm:
    """Класс, моделирующий поведение робота-манипулятора с хватом.
    
    Положение манипулятора в пространстве определяется начальной
    точкой с координатами x, y, z и набором последовательно 
    соединенных звеньев, имеющих длину L, угол между звеном и осью
    Z phi и угол между звеном и плоскостью xOy theta."""
    
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.origin = Vertex(x, y, z)
        self.edges = []

    def __str__(self):
        ret = 'Edges:\n' + '\n'.join(list(map(lambda e: e.__str__(), self.edges)))
        ret = ret + '\nVertices:\n' + '\n'.join(list(map(lambda v: v.__str__(), self.calculate_vertices())))
        return ret
    
    """Добавляет звено"""
    def append_edge(self, L, p, th):
        self.edges.append(Edge(L, p, th))

    """Возвращает положение сочленений звеньев"""
    def calculate_vertices(self):
        ret = [self.origin]
        for edge in self.edges:
            new_x = ret[-1].x + edge.L*sin(edge.phi)*cos(edge.theta)
            new_y = ret[-1].y + edge.L*sin(edge.phi)*sin(edge.theta)
            new_z = ret[-1].z + edge.L*cos(edge.phi)
            ret.append(Vertex(new_x, new_y, new_z))
        return ret

    """Возвращает положение хвата (последнее звено)"""
    def calculate_grip(self):
        return calculate_vertices()[-1]

    def rotate_z(self, nedge, angle):
        for edge in self.edges[nedge::1]:
            edge.rotate_z(angle)

    def rotate_xy(self, nedge, angle):
        for edge in self.edges[nedge::1]:
            edge.rotate_xy(angle)

    """Параллельный перенос модели"""
    def move(self, dx, dy, dz):
        self.origin.x += dx
        self.origin.y += dy
        self.origin.z += dz
    
if __name__ == "__main__":
    r = RoboticArm()
    r.append_edge(2, pi/4, pi/2)
    r.append_edge(2, 0, pi/2)
    print(r)

    r.rotate_z(0, pi/4)
    print(r)
