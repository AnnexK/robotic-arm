import solver
import writer

print('Building graph...')
G = solver.ExampleGraphBuilder(30,30,30).make_graph()

S = solver.AntSolver(G, (10,2,3), (15,22,25),
                     a=1.0,
                     b=1.0,
                     q=5.0,
                     rho=0.01,
                     base_pheromone=0.01)

print('Solving...')
best, worst, avg = S.solve(iters=50, ants_n=10)

name = input('Input file name to save:')

w = writer.ColumnWriter(open(name, 'w', newline=''), ' ')
w.write(best,worst,avg)

