from math import sin, cos, sqrt, isclose

def isclose_wrap(a, b):
    """Обертка для сравнения двух чисел с плавающей точкой"""
    eps = 1e-9 # можно менять
    return isclose(a, b, abs_tol=eps)

def linear_equation(x, y, phi):
    """Возвращает коэффициенты линейного уравнения прямой по н. т. (x0, y0)
и углу отн. Ox phi"""
    s = sin(phi)
    c = cos(phi)
    
    return [-s, c, s * x - c * y]

def linear_equation_segment(x1, y1, x2, y2):
    """Возвращает коэффициенты прямой, содержащий отрезок [(x1, y1); (x2, y2)]"""
        
    x = x2-x1
    y = y2-y1
    
    if isclose_wrap(x, 0.0) and isclose_wrap(y, 0.0):
        raise ValueError("Через отрезок невозможно построить прямую")
    
    return [-y, x, y * x1 - x * y1]

def linear_solve(e1, e2):
    """Возвращает None, если у системы линейных уравнений e1, e2 нет решений,
(), если у e1, e2 бесконечное число решений,
(x, y), если у e1, e2 одно решение"""

    
    if isclose_wrap(e1[0]*e2[1], e1[1]*e2[0]):
        if isclose_wrap(e1[0]*e2[2], e1[2]*e2[0]) and isclose_wrap(e1[1]*e2[2], e1[2]*e2[1]): # совпадают
            return ()
        else: # параллельны
            return None
    else:
        denom = e1[0]*e2[1] - e2[0]*e1[1]
        x = (e2[2]*e1[1]-e1[2]*e2[1]) / denom
        y = (e2[0]*e1[2]-e1[0]*e2[2]) / denom
        return (x, y)

def quad_solve(a, b, c):
    """Возвращает действ. корни уравнения ax^2 + bx + c = 0"""
    d = b ** 2 - 4 * a * c

    if isclose_wrap(d, 0.0):
        return [-b / (2.0 * a)]
    elif d > 0.0:
        d = sqrt(d)
        return [(-b + d) / (2.0 * a), (-b - d) / (2.0 * a)]
    else:
        return []

def linear_circle_solve(lin_eq, circle_eq):
    xr = circle_eq[0]
    yr = circle_eq[1]
    R = sqrt(circle_eq[2])
    
    if isclose_wrap(lin_eq[1],0.0): # прямая параллельна Oy
        x0 = lin_eq[2] / -lin_eq[0]
        roots = quad_solve(1.0, -2 * yr, yr ** 2 + (x0 - xr) ** 2 - R ** 2)
        points = [[x0, r] for r in roots]
    elif isclose_wrap(lin_eq[0],0.0): # прямая параллельна Ox
        y0 = lin_eq[2] / -lin_eq[1]
        roots = quad_solve(1.0, -2 * xr, xr ** 2 + (y0 - yr) ** 2 - R ** 2)
        points = [[r, y0] for r in roots]
    else: # общий случай (подставить y)
        c = xr ** 2 + yr ** 2 - R ** 2
        
        k = (lin_eq[2] + lin_eq[1]) / -lin_eq[0]

        a = 1 + k ** 2
        b = -2 * (yr + xr * k) 
    
        roots = quad_solve(a, b, c)
        points = [[k * r, r] for r in roots]
    
    return points # точки на основании
