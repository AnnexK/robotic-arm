import writer

from solver.ants.ant import Ant
from solver.aco_algorithms.ant_system import AntSystem
from solver.solver import AntSolver

from solver.graph_builders.graph_builder import ExampleGraphBuilder
from plotter.plotter import Plot

from logger import log


# функции, проверяющие значения вводимых данных
# (валидаторы)
def gz_float(r):
    try:
        v = float(r)
        return v if 0.0 < v else None
    except ValueError:
        return None


def gz_int(r):
    try:
        v = int(r)
        return v if 0 < v else None
    except ValueError:
        return None


def gz_dim(r):
    t = eval(r)  # грубо-то как
    if type(t) is not tuple or len(t) != 3:
        return None
    for d in t:
        if type(d) is not int or d <= 0:
            return None

    return t


def gz_vertex(r, dim):
    t = eval(r)
    if type(t) is not tuple or len(t) != 3:
        return None
    for c, d in zip(t, dim):
        if type(c) is not int or not (0 <= c < d):
            return None

    return t


def rho_bound(r):
    try:
        v = float(r)
        return v if 0.0 < v < 1.0 else None
    except ValueError:
        return None


# параметры, их значения по умолчанию и валидаторы
vals = {'a': {'value': 1.0, 'validator': gz_float},
        'b': {'value': 1.0, 'validator': gz_float},
        'dims': {'value': (30, 30, 30), 'validator': gz_dim},
        'start':
        {
            'value': (0, 0, 0),
            'validator': lambda r: gz_vertex(r, vals['dims']['value'])
        },
        'end':
        {
            'value': (29, 29, 29),
            'validator': lambda r: gz_vertex(r, vals['dims']['value'])
        },
        'phi': {'value': 1e-5, 'validator': gz_float},
        'rho': {'value': 2e-1, 'validator': rho_bound},
        'q': {'value': 1.0, 'validator': gz_float},
        'n': {'value': 50, 'validator': gz_int},
        'i': {'value': 64, 'validator': gz_int}}

# формат входного файла:
# каждая строка:
# <имя_параметра>=<значение_параметра>,
# где <имя_параметра> -- один из
# a - alpha, параметр, регулирующий влияние феромона
# b - beta, параметр, регулирующий влияние эвр. данных (вес ребра)
# rho - скорость испарения феромона
# phi - базовый уровень феромона
# q - суммарное кол-во феромона, откладываемое муравьем
# n - количество муравьев
# i - количество итераций
# dims - размерности графа (x, y, z)
# start - начальная точка
# end - конечная точка

# если одного из параметров в файле не будет найдено,
# то будет использоваться значение по умолчанию

# пример входного файла -- test.tst в корне
# открывать любым текстовым редактором

# программа запрашивает имя файла
with open(input('Введите имя файла с параметрами: '), 'r') as fp:
    for s in fp.readlines():
        arg, val = s.split('=')
        validated = vals[arg]['validator'](val)
        if validated is not None:
            vals[arg]['value'] = validated
        else:
            raise ValueError('Wrong value read')

# вывод введенных параметров
# (не используется)
for k in vals:
    log()['ST_READER'].log(str(vals[k]['value']))


log()['MAIN'].log('Creating solver...')
G, start, end = ExampleGraphBuilder(
    # размеры графа
    vals['dims']['value'],
    # начальная точка
    vals['start']['value'],
    # конечная точка
    vals['end']['value'],
    # базовый уровень феромона
    vals['phi']['value']).make_graph()

# a - муравей
# параметры:
# коэф. привлекательности по кол-ву феромона на ребре;
# коэф. привлекательности по весу ребра;
# "сила" муравья (суммарное кол-во откладываемого феромона);
# граф, на котором происходит поиск решения;
# начальная точка
a = Ant(vals['a']['value'],
        vals['b']['value'],
        G,
        vals['start']['value'])

# S - объект конкретной реализации алгоритма м.к. (стратегия)
# параметры:
# граф;
# конечная точка;
# скорость испарения (от 0 до 1)
S = AntSystem(G,
              vals['q']['value'],
              vals['end']['value'],
              vals['rho']['value'])

# задание муравья для создания новых
S.set_proto(a)

# sol - объект, осуществляющий решение задачи
# с помощью объекта-алгоритма
# параметр: объект реализации алгоритма
sol = AntSolver(S)
log()['MAIN'].log('Solving...')

# возвращает длину
# лучшего глобального пути,
# длину худшего пути на итерации и
# средние длины путей для каждой итерации,
# а также лучший найденный путь
# iters - кол-во итераций, ants_n - кол-во муравьев
best, worst, average, path = sol.solve(iters=vals['i']['value'],
                                       ants_n=vals['n']['value'])

log()['MAIN'].log('Solving complete.')
# запрашивает имя файла для записи лучших, худших
# и средних длин пути
with writer.ColumnWriter(input('input filename for stats: '),
                         ' ') as w:
    w.write(best, worst, average)

# запрашивает имя файла для записи лучшего пути
with writer.PlainWriter(input('input filename for solution: ')) as w:
    w.write(path)

log()['MAIN'].log('Plotting...')
# строит графики
# (нужна библиотека matplotlib)
# (установка: pip install matplotlib)
# (или py -m pip install matplotlib)
p = Plot()
p.plot(best, worst, average)
