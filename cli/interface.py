import csv

import solver
import env

# значения ключей по умолчанию

default = {'-t' : None,
           '-a' : 1.0,
           '-b' : 1.0,
           '-q' : 1.0,
           '-p' : 0.1,
           '-d' : 0.1,
           '-k' : 1,
           '-i' : 1,
           '-o' : None}

def parse_args(argv):
    """Возвращает словарь значений из аргументов командной строки"""
    dct = {}
    for i in range(1,len(args),2):
        key, value = argv[i], argv[i+1]
        if not key in dct: # ключа нет в разбираемом словаре
            if not key in default: # и нет в словаре по умолчанию
                raise ValueError('error: unknown key ' + key)
            dct[key] = value
        else: # дубликат
            raise ValueError('error: key duplicate encountered')

    # записать в возвр. словарь умолчания, если их не передали
    ret = dict(default)
    ret.update(dct)
    return ret

def main(argv):
    """Основная функция программы, принимает список аргументов
командной строки"""

    # разбор аргументов
    try:
        parsed = parse_args(argv)
    except IndexError:
        print('error: insufficient arg values')
        exit()
    except ValueError as err:
        print(err)
        exit()

    # преобразование аргументов
    try:
        alpha = float(parsed['-a'])
        beta = float(parsed['-b'])
        q = float(parsed['-q'])
        base_phero = float(parsed['-p'])
        decay = float(parsed['-d'])
        ants_n = int(parsed['-k'])
        iters = int(parsed['-i'])
    except ValueError:
        print('error: unable to convert some of the values')

    # чтение данных задачи
    try:
        R, Env, endpoint = env.load_task(parsed['-t'])
    except OSError:
        print('error: cannot open file', parsed['-t'])
        exit()
    except TypeError:
        print('error: task file not provided')
        exit()

    # решение задачи
    S = solver.Solver(R, endpoint, alpha, beta, q, decay, base_phero)
    best, worst, avg = S.solve(ants_n, iters)

    # запись результатов в файл
    try:
        with open(parsed['-o'], "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows([best, worst, avg])
    except TypeError:
        print('error: output file not provided')
        exit()
    except OSError:
        print('error: cannot open file', parsed['-o'])
        exit()
        
