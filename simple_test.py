import writer
from solver.ants.ant import Ant
from solver.aco_algorithms.simple_aco import SimpleACO
from solver.solver import AntSolver

from solver.builders.graph_builder import ExampleGraphBuilder
from plotter.plotter import Plot


print('Building graph...')
G, start, end = ExampleGraphBuilder(
    # размеры графа
    30, 30, 30,
    # начальная точка
    (10, 2, 3),
    # конечная точка
    (22, 14, 28),
    # базовый уровень феромона
    1e-5).make_graph()

# a - муравей
# параметры:
# коэф. привлекательности по кол-ву феромона на ребре;
# коэф. привлекательности по весу ребра;
# "сила" муравья (суммарное кол-во откладываемого феромона);
# граф, на котором происходит поиск решения;
# начальная точка
a = Ant(1.0, 1.0, 1.0, G, start)

# S - объект конкретной реализации алгоритма м.к. (стратегия)
# параметры:
# граф;
# конечная точка;
# скорость испарения (от 0 до 1)
S = SimpleACO(G, end, 1e-2)

# задание муравья для создания новых
S.set_proto(a)

# sol - объект, осуществляющий решение задачи
# с помощью объекта-алгоритма
# параметр: объект реализации алгоритма
sol = AntSolver(S)
print('Solving...')

# возвращает длины лучших, худших,
# средние длины путей для каждой итерации,
# а также лучший найденный путь
# iters - кол-во итераций, ants_n - кол-во муравьев
best, worst, average, path = sol.solve(iters=50, ants_n=64)

# запрашивает имя файла для записи лучших, худших
# и средних длин пути
with writer.ColumnWriter(input('input filename for stats: '),
                         ' ') as w:
    w.write(best, worst, average)

# запрашивает имя файла для записи лучшего пути
with writer.PlainWriter(input('input filename for solution: ')) as w:
    w.write(path)

# строит графики
# (нужна библиотека matplotlib)
# (установка: pip install matplotlib)
# (или py -m pip install matplotlib)
p = Plot()
p.plot(best, worst, average)
