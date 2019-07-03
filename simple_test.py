import solver
import cli.csv_writer as writer

print('Building graph...')
G = solver.ExampleGraphBuilder(12,12,12).make_graph()

S = solver.AntSolver(G, (1,2,3), (7,8,8),
                     a=1.0,
                     b=1.0,
                     q=1000.0,
                     rho=0.01,
                     base_pheromone=0.01)

print('Solving...')
best, worst, avg = S.solve(iters=50, ants_n=10)

print('Input file name to save:')
name = input()

w = writer.ColumnWriter(open(name, 'w', newline=''), ' ')
w.write(best,worst,avg)

