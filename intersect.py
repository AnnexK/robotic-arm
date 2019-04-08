from math import sin, cos, sqrt
from common_math import * # f_isclose
import geometry as geom
import robot

def robot_linear(robot):
    """Возвращает коэффициенты линейного уравнения прямой по н. т. (x0, y0)
и углу отн. Ox"""
    s = sin(robot.angle)
    c = cos(robot.angle)
    x0 = robot.origin.x
    y0 = robot.origin.y
    
    return [-s, c, s * x0 - c * y0]

def quad_solve(a, b, c):
    """Возвращает действ. корни уравнения ax^2 + bx + c = 0"""
    d = b ** 2 - 4 * a * c

    if f_isclose(d, 0.0):
        return [-b / (2.0 * a)]
    elif d > 0.0:
        d = sqrt(d)
        return [(-b + d) / (2.0 * a), (-b - d) / (2.0 * a)]
    else:
        return []

def segment_linear(seg):
    """Возвращает коэффициенты прямой, содержащий отрезок [(x1, y1); (x2, y2)]"""
    vec = seg.make_vector()
    len = vec.length()
    if (f_isclose(len, 0.0)):
        raise ValueError("Невозможно однозначно построить прямую, содержащую данный отрезок")
    
    x = vec.x
    y = vec.y

    s = y / len
    c = x / len

    # н. т.
    x1 = seg._points[0].x
    y1 = seg._points[0].y
    
    return [-s, c, s * x1 - c * y1]

def linear_solution(e1, e2):
    """Возвращает None, если у системы линейных уравнений e1, e2 нет решений,
(), если у e1, e2 бесконечное число решений,
(x, y), если у e1, e2 одно решение"""

    
    if f_isclose(e1[0]*e2[1], e1[1]*e2[0]):
        if f_isclose(e1[0]*e2[2], e1[2]*e2[0]) and f_isclose(e1[1]*e2[2], e1[2]*e2[1]): # совпадают
            return ()
        else: # параллельны
            return None
    else:
        denom = e1[0]*e2[1] - e2[0]*e1[1]
        x = (e2[2]*e1[1]-e1[2]*e2[1]) / denom
        y = (e2[0]*e1[2]-e1[0]*e2[2]) / denom
        return (x, y)
    
def circle_intersect(robot, rot_obj):
    lcoeff = robot_linear(robot)

    y0 = robot.origin.y
    x0 = robot.origin.x
    
    yr = rot_obj.base_point.y
    xr = rot_obj.base_point.x
    R = rot_obj.radius
    
    if f_isclose(lcoeff[1],0.0): # прямая параллельна Oy
        roots = quad_solve(1.0, -2 * yr, yr ** 2 + (x0 - xr) ** 2 - R ** 2)
        points = [[x0, r] for r in roots]
    elif f_isclose(lcoeff[0],0.0): # прямая параллельна Ox
        roots = quad_solve(1.0, -2 * xr, xr ** 2 + (y0 - yr) ** 2 - R ** 2)
        points = [[r, y0] for r in roots]
    else: # общий случай (подставить y)
        c = xr ** 2 + yr ** 2 - R ** 2
        
        k = (lcoeff[2] + lcoeff[1]) / -lcoeff[0]

        a = 1 + k ** 2
        b = -2 * (yr + xr * k) 
    
        roots = quad_solve(a, b, c)
        points = [[k * r, r] for r in roots]
    
    return [geom.Point(x, y, rot_obj.base_point.z) for x, y in points] # точки на основании

def rectangle_intersect(robot, piped):
    plane_eq = robot_linear(robot)

    segments = [piped.make_segment(0,1),
                piped.make_segment(1,2),
                piped.make_segment(2,3),
                piped.make_segment(3,0)]
    seg_eq = map(segment_linear, segments) # получить список уравнений из списка отрезков
    ret = []
    testing = [True, True, True, True] # какие отрезки проверять
    
    for i, eq in enumerate(seg_eq):
        solution = linear_solution(plane_eq, eq) # найти пересечение
        if not solution and solution is not None: # совпадают
            seg_points = segments[i]._points
            return [geom.Point(seg_points[0].x, seg_points[0].y, seg_points[0].z),
                    geom.Point(seg_points[1].x, seg_points[1].y, seg_points[1].z)]
        elif solution is None: # параллельны
            continue
        elif not testing[i]: # не проверять текущий отрезок
            continue
        else:
            lx = min(segments[i]._points[0].x, segments[i]._points[1].x)
            rx = max(segments[i]._points[0].x, segments[i]._points[1].x)
            ly = min(segments[i]._points[0].y, segments[i]._points[1].y)
            ry = max(segments[i]._points[0].y, segments[i]._points[1].y)

            # принадлежит ли точка отрезку?
            if lx < solution[0] < rx or f_isclose(lx, solution[0]) or f_isclose(rx, solution[0]):
                if ly < solution[1] < ry or f_isclose(ly, solution[1]) or f_isclose(ry, solution[1]):
                    ret.append(geom.Point(solution[0], solution[1], piped._points[0].z))
            # точка пересечения на границе отрезка
            # -> другой отрезок тоже пересекает прямую в этой плоскости
            if ret and segments[i]._points[0] == ret[-1]:
                testing[(i-1)%4] = False                
            if ret and segments[i]._points[1] == ret[-1]:
                testing[(i+1)%4] = False

    return ret
