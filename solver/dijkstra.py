import heapq

def dijkstra(G, start, end):
    X = G.x_nedges + 1
    Y = G.y_nedges + 1
    Z = G.z_nedges + 1

    # прямая и обратная ф. для отображения кортежей в числа и наоборот
    f = lambda t : t[0] + t[1] * X + t[2] * X * Y
    invf = lambda k : (k % X, (k % (X*Y)) // X, k // (X*Y))

    # расстояния
    d = [inf for i in range(X*Y*Z)]
    d[f(start)] = 0.0

    # очередь с приоритетами
    heap = [(0.0, start)]
    # предки вершин
    p = [None for i in range(0, X*Y*Z)]

    cur = None
    dest = end

    while heap:
        # достать вершину с минимальным расстоянием из очереди
        weight, cur = heapq.heappop(heap)
        if cur == dest: # найден нужный путь
            break

        for w in G.get_adjacent(cur):
            # индексы в массиве расстояний
            fw = f(w)
            fcur = f(cur)
            edge = G[cur,w]
            if edge is not None and d[fw] > d[fcur] + edge.weight:
                d[fw] = d[fcur] + edge.weight
                heapq.heappush(heap, (d[fw], w))
                p[fw] = cur

    path = [dest]
    i = f(path[0])

    if d[i] == inf:
        return None
    
    while p[i] is not None:
        path.append(p[i])
        i = f(path[-1])
    
    return (d[f(dest)], path)
