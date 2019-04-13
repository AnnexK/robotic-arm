from math import sin, cos, sqrt
from collections import deque
from copy import copy

from common_math import * # всякая математика
import geometry as geom
import robot

from numpy import arange

def robot_linear(robot):
    """Возвращает коэффициенты линейного уравнения прямой по н. т. (x0, y0)
и углу отн. Ox"""
    return linear_equation(robot.origin.x, robot.origin.y, robot.angle)

def segment_linear(seg):
    """Возвращает коэффициенты прямой, содержащий отрезок"""
    return linear_equation_segment(seg._points[0].x, seg._points[0].y,
                                   seg._points[1].x, seg._points[1].y)
    
def circle_intersect(robot, rot_obj):
    """Возвращает точки пересечения прямой-проекции плоскости робота на xOy
и окружности-проекции тела вращения на xOy"""
    linear = robot_linear(robot) # прямая

    points = linear_circle_solve(linear,
                                 [rot_obj.base_point.x, rot_obj.base_point.y, rot_obj.radius ** 2])

    return [geom.Point(x, y, rot_obj.base_point.z) for x, y in points] # точки на основании

def point_in_segment(seg, x, y):
    """Возвращает принадлежность точки (x, y) отрезку (geom.Segment) seg
Assert: точка лежит на той же прямой, что и отрезок"""
    lx = min(seg[i]._points[0].x, seg[i]._points[1].x)
    rx = max(seg[i]._points[0].x, seg[i]._points[1].x)
    ly = min(seg[i]._points[0].y, seg[i]._points[1].y)
    ry = max(seg[i]._points[0].y, seg[i]._points[1].y)

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
        solution = linear_solve(plane_eq, eq) # найти пересечение
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
        dist_from_center = sqrt((pivot[0] - c_origin.x) ** 2 + (pivot[1] - c_origin.y) ** 2)
        dist_sect = R * (1 - h_pl/h) # расстояние от центра до плоскости сечения

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
        
