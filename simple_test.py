import writer
from solver.ants.ant import Ant
from solver.aco_algorithms.simple_aco import SimpleACO
from solver.solver import AntSolver

from solver.builders.graph_builder import ExampleGraphBuilder

print('Building graph...')
G, start, end = ExampleGraphBuilder(
    30, 30, 30,
    (10, 2, 3),
    (22, 14, 28),
    1e-5).make_graph()

a = Ant(1.0, 1.0, 1.0, G, start)
S = SimpleACO(G, end, 1e-2)
S.set_proto(a)

sol = AntSolver(S)
print('Solving...')
best, worst, average, path = sol.solve(iters=5, ants_n=64)

with writer.ColumnWriter('simple.csv', ' ') as w:
    w.write(best, worst, average)

for v in path:
    print(v)
