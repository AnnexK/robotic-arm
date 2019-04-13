from math import sin, cos, sqrt, pi
from collections import deque
from copy import copy

import common_math as cm # всякая математика
from common_math import isclose_wrap

import geometry as geom
import robot

from numpy import arange

def robot_linear(robot):
    """Возвращает коэффициенты линейного уравнения прямой по н. т. (x0, y0)
и углу отн. Ox"""
    return cm.linear_equation(robot.origin.x, robot.origin.y, robot.angle)

def segment_linear(seg):
    """Возвращает коэффициенты прямой, содержащий отрезок"""
    return cm.linear_equation_segment(seg._points[0].x, seg._points[0].y,
                                      seg._points[1].x, seg._points[1].y)
    
def circle_intersect(robot, rot_obj):
    """Возвращает точки пересечения прямой-проекции плоскости робота на xOy
и окружности-проекции тела вращения на xOy"""
    linear = robot_linear(robot) # прямая

    points = cm.linear_circle_solve(linear,
                                    [rot_obj.base_point.x, rot_obj.base_point.y, rot_obj.radius ** 2])

    return [geom.Point(x, y, rot_obj.base_point.z) for x, y in points] # точки на основании

def point_in_segment(seg, x, y):
    """Возвращает принадлежность точки (x, y) отрезку (geom.Segment) seg
Assert: точка лежит на той же прямой, что и отрезок"""
    lx = min(seg._points[0].x, seg._points[1].x)
    rx = max(seg._points[0].x, seg._points[1].x)
    ly = min(seg._points[0].y, seg._points[1].y)
    ry = max(seg._points[0].y, seg._points[1].y)

    x_in = lx < x < rx or isclose_wrap(lx, x) or isclose_wrap(rx, x)
    y_in = ly < y < ry or isclose_wrap(ly, y) or isclose_wrap(ry, y)
    # принадлежит ли точка отрезку?
    return x_in and y_in

def rectangle_intersect(robot, piped):
    """Возвращает точки пересечения проекции плоскости робота на xOy и проекции
прямоугольного параллелепипеда на xOy"""
    plane_eq = robot_linear(robot) # прямая робота

    segments = [piped.make_segment(0,1), # отрезки в порядке обхода
                piped.make_segment(1,2),
                piped.make_segment(2,3),
                piped.make_segment(3,0)]
    seg_eq = map(segment_linear, segments) # получить список уравнений из списка отрезков
    ret = []
    testing = [True, True, True, True] # какие отрезки проверять
    
    for i, eq in enumerate(seg_eq):
        solution = cm.linear_solve(plane_eq, eq) # найти пересечение
        if not solution and solution is not None: # совпадают (возвращен пустой кортеж)
            seg_points = segments[i]._points
            return [geom.Point(seg_points[0].x, seg_points[0].y, seg_points[0].z),
                    geom.Point(seg_points[1].x, seg_points[1].y, seg_points[1].z)]
        elif solution is None: # параллельны (возвращено None)
            continue
        elif not testing[i]: # не проверять текущий отрезок
            continue
        else: # пересекаются (возвращен кортеж с координатами)
            if point_in_segment(segments[i], solution[0], solution[1]):
                ret.append(geom.Point(solution[0], solution[1], piped._points[0].z))
                # точка пересечения на границе отрезка
                # -> другой отрезок тоже пересекает прямую в этой плоскости
                if ret and segments[i]._points[0] == ret[-1]:
                    testing[(i-1)%4] = False                
                if ret and segments[i]._points[1] == ret[-1]:
                    testing[(i+1)%4] = False

    return ret

def build_rectangle(base_points, height_vector):
    """Построение прямоугольника - сечения параллелепипеда/цилиндра плоскостью,
по точкам пересечения проекций и вектору высоты
base_points - массив geom.Point, height_vector - объект geom.Point"""
    if base_points == []: # нет точек - нет отрезков
        return []
    elif len(base_points) == 1: # одна точка - один отрезок
        p = base_points[0]
        return [geom.Segment(p.x, p.y, p.z, p.x, p.y, p.z+height_vector.z)]
    else: # две точки - четыре отрезка
        # мб и не очень эффективно
        points = deque([base_points[0],
                        base_points[0] + height_vector,
                        base_points[1] + height_vector,
                        base_points[1]])
        
        c_points = copy(points)
        c_points.rotate(-1)
        
        ret = list(map(lambda s, e: geom.Segment(s.x, s.y, s.z, e.x, e.y, e.z),
                       points, c_points))
        return ret

def build_hyperbola(base_points, cone):
    """Приблизительное построение гиперболы - сечения конуса/усеченного конуса плоскостью
по точкам пересечения проекций и векторам конуса
base_points - массив geom.Point, cone - объект geom.Cone"""
    R = cone.radius
    h = cone.height
    h_pl = cone.second_height

    steps = 10 # количество шагов для получения точек; 
    
    if base_points == []:
        return []
    elif len(base_points) == 1: # одна точка - одна точка (как отрезок с началом и концом в одной точке)
        p = base_points[0]
        return geom.Segment(p.x, p.y, p.z, p.x, p.y, p.z)
    else: # две точки - набор отрезков
        p1 = base_points[0]
        p2 = base_points[1]
        
        pivot = [(p1.x+p2.x)/2, (p1.y+p2.y)/2] # вершина гиперболы
        c_origin = cone._points[0]
        # расстояние от центра до плоскости сечения, параллельной Oz
        dist_from_center = sqrt((pivot[0] - c_origin.x) ** 2 + (pivot[1] - c_origin.y) ** 2) 
        dist_sect = R * (1 - h_pl/h) # расстояние от центра до плоскости сечения усеченного конуса

        lin_eq = linear_equation_segment(p1.x, p1.y, p2.x, p2.y)

        dist_limit = max(dist_from_center, dist_sect)

        hyp_points = deque()
        
        for d in arange(dist_limit, R, (R-dist_limit)/steps):
            pts = linear_circle_solve(lin_eq, [c_origin.x, c_origin.y, d ** 2])
            ptsh = h * (1 - d/R) # высота полученных точек
            hyp_points.appendleft(geom.Point(pts[0][0], pts[0][1], c_origin.z + ptsh))
            if len(pts) == 2:
                hyp_points.append(geom.Point(pts[1][0], pts[1][1], c_origin.z + ptsh))

        hyp_points.appendleft(geom.Point(p1.x, p1.y, p1.z))
        hyp_points.append(geom.Point(p2.x, p2.y, p2.z))
        
        hyp_points_shl = copy(hyp_points)
        hyp_points_shl.rotate(-1)

        ret = list(map(lambda s, e: geom.Segment(s.x, s.y, s.z, e.x, e.y, e.z),
                       hyp_points, hyp_points_shl))
        return ret
        

def plane_intersect(seg, plane):
    """Проверяет пересечение отрезка и плоскости"""

    p1 = seg._points[0]
    p2 = seg._points[1]

    # векторы от точки на плоскости до точек отрезка
    v1 = p1 - plane._points[1]
    v2 = p2 - plane._points[1]

    n = plane._points[0]

    # скалярные произведения
    dp1 = n * v1
    dp2 = n * v2

    # если одно из сп равно 0, то одна из точек отрезка в плоскости
    # если у сп разные знаки, то точки находятся по разные стороны от плоскости
    return isclose_wrap(dp1, 0.0) or isclose_wrap(dp2, 0.0) or dp1 * dp2 < 0.0

def segment_intersect(seg1, seg2):
    """Проверяет пересечение двух отрезков (geom.Segment) в плоскости xOy"""
    
    return cm.segment_intersect([[seg1._points[0].x, seg1._points[0].y],
                                 [seg1._points[1].x, seg1._points[1].y]],
                                [[seg2._points[0].x, seg2._points[0].y],
                                 [seg2._points[1].x, seg2._points[1].y]])
    
def polygon_intersect(seg, seg_seq, phi):
    """Проверяет пересечение отрезка и многоугольника, представленного последовательностью
отрезков"""
    rotmat = geom.TSR(p=-phi, ps=pi/2) # проекция плоскости на xOy
    
    seg.apply_transform(rotmat)
    
    for s in seg_seq:
        s.apply_transform(rotmat)
        if segment_intersect(s, seg):
            return True

    return False

def build_segments(robot):
    V = robot.calculate_vertices()

    ret = []
    for i in range(0, len(V)-1):
        ret.append(geom.Segment(V[i].x, V[i].y, V[i].z, V[i+1].x, V[i+1].y, V[i+1].z))

    return ret

def intersect_object(robot, gobj):
    rseg = build_segments(robot)

    phi = robot.angle
    
    for s in rseg:
        if type(gobj) == geom.Plane:
            if plane_intersect(s, gobj):
                return True
        elif type(gobj) == geom.Parallelepiped:
            base = rectangle_intersect(robot, gobj)
            vec = gobj.make_segment(0, 4).make_vector()
            poly = build_rectangle(base, vec)
            if polygon_intersect(s, poly, phi):
                return True
        elif type(gobj) == geom.Cylinder:
            base = circle_intersect(robot, gobj)
            vec = gobj._points[1]
            poly = build_rectangle(base, vec)
            if polygon_intersect(s, poly, phi):
                return True
        elif type(gobj) == geom.Cone:
            base = circle_intersect(robot, gobj)
            poly = build_hyperbola(base, gobj)
            if polygon_intersect(s, poly, phi):
                return True
        else:
            raise ValueError("Передан объект, для которого нет обработчика")

    return False

def intersect(robot, gobj_seq):
    for obj in gobj_seq:
        if intersect_object(robot, obj):
            return True
    return self_intersect(robot)

def self_intersect(robot):
    rseg = build_segments(robot)

    k = len(rseg)
    # 1. соседние звенья пересекаются только в точке сочленения
    # 2. если звено i пересекает звено j, то и звено j пересекает звено i
    for i in range(0, k-2):
        for j in range(i+2, k):
            if segment_intersect(rseg[i], rseg[j]):
                return True
    return False
