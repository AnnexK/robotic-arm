from math import isclose

def f_isclose(a, b):
    """Обертка для сравнения двух чисел с плавающей точкой"""
    eps = 1e-9 # можно менять
    return isclose(a, b, abs_tol=eps)
