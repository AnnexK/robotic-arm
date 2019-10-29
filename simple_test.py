import writer

from solver.ants.ant import Ant
from solver.aco_algorithms import AntSystem, ElitistAS, ASRank
from solver.solver import AntSolver

from gridgraph import GridGraph
from gridgraph.weight_calcs.const import BoundedConstWeight
from gridgraph.phi_managers.base import PhiManager
# для MMAS, не используется
from gridgraph.phi_managers.bounded import BoundedPhiManager

from plotter.plotter import Plot

from logger import log


def as_builder(params):
    g = GridGraph(BoundedConstWeight(params['dims'],
                                     1.0),
                  PhiManager(params['phi']))

    a = Ant(params['a'],
            params['b'],
            g,
            params['start'])

    S = AntSystem(g, params['Q'],
                  params['end'],
                  params['rho'])

    S.set_proto(a)
    return S


def eas_builder(params):
    g = GridGraph(BoundedConstWeight(params['dims'],
                                     1.0),
                  PhiManager(params['phi']))

    a = Ant(params['a'],
            params['b'],
            g,
            params['start'])

    S = ElitistAS(g, params['Q'],
                  params['end'],
                  params['rho'],
                  params['Qe'])

    S.set_proto(a)
    return S


def asrank_builder(params):
    g = GridGraph(BoundedConstWeight(params['dims'],
                                     1.0),
                  PhiManager(params['phi']))

    a = Ant(params['a'],
            params['b'],
            g,
            params['start'])

    S = ASRank(g, params['Q'],
               params['end'],
               params['rho'],
               params['w'])

    S.set_proto(a)
    return S


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


# имена алгоритмов
alg_builders = {'antsystem': as_builder,
                'elitist': eas_builder,
                'asrank': asrank_builder, }


def alg_name(s):
    return s if any(s == n for n in alg_builders) else None


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
        'Q': {'value': 1.0, 'validator': gz_float},
        'n': {'value': 50, 'validator': gz_int},
        'i': {'value': 64, 'validator': gz_int},
        'alg': {'value': 'antsystem', 'validator': alg_name},
        'Qe': {'value': 1.0, 'validator': gz_float},
        'w': {'value': 50, 'validator': gz_int}, }

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
# alg - имя алгоритма

# Qe - количество феромона, откладываемого на лучшем пути
# (для EAS)

# w - количество ранжируемых муравьев
# (для ASrank)

# если одного из параметров в файле не будет найдено,
# то будет использоваться значение по умолчанию

# пример входного файла -- test.tst в корне
# открывать любым текстовым редактором

# программа запрашивает имя файла
with open(input('Введите имя файла с параметрами: '), 'r') as fp:
    for s in fp.readlines():
        s = s.strip()
        arg, val = s.split('=')
        validated = vals[arg]['validator'](val)
        if validated is not None:
            vals[arg]['value'] = validated
        else:
            raise ValueError('Wrong value read: {}'
                             .format(arg))

params = {k: vals[k]['value'] for k in vals if k != 'alg'}
alg = vals['alg']['value']

# вывод введенных параметров
# (не используется)
for k in vals:
    log()['ST_READER'].log(str(vals[k]['value']))


log()['MAIN'].log('Creating solver...')
sol = AntSolver(alg_builders[alg](params))
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
