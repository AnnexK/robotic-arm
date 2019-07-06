import solver
import writer

print('Building graph...')
G, start, end = solver.ExampleGraphBuilder(30,30,30,
                                           s=(10,2,3),
                                           e=(15,22,25),
                                           base=0.01).make_graph()

S = solver.AntSolver(G, start, end,
                     a=1.0,
                     b=1.0,
                     q=500.0,
                     rho=0.01)

print('Solving...')
best, worst, avg = S.solve(iters=50, ants_n=64)

name = input('Input file name to save:')

w = writer.ColumnWriter(open(name, 'w', newline=''), ' ')
w.write(best,worst,avg)
del w # закрытие файла
