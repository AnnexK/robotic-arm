import solver
import csv

print('Building graph...')
G = solver.ExampleGraphBuilder(120,120,120).make_graph()
S = solver.AntSolver(G, (1,2,3), (12,14,24), q=1000.0)
print('Solving...')
best, worst, avg = S.solve(iters=20, ants_n=10)
print(best, worst, avg)
