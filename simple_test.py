import solver

print('Building graph...')
G = solver.ExampleGraphBuilder(50,50,50).make_graph()
S = solver.AntSolver(G, (1,2,3), (4,4,4), q=1000.0)
print('Solving...')
best, worst, avg = S.solve(iters=20, ants_n=10)
print(best, worst, avg)
