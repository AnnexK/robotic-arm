from graphs.prm.metrics.metric import Metric
from .nearest import KNearest
from math import inf
from typing import List, Optional, Sequence, Tuple
from env.types import State
from graphs.prm.metrics.euclid import EuclideanMetric
from util.quickselect import quickselect
import heapq as heap



class KDTree(KNearest):
    class KDNode:
        def __init__(self, val: State):
            self.val: State = val
            self.left: Optional[KDTree.KDNode] = None
            self.right: Optional[KDTree.KDNode] = None
    Node = Optional[KDNode]

    def __init__(self, dim: int, states: List[State] = []):
        self.dim = dim
        self.inf = tuple(inf for _ in range(dim))
        self._metric = EuclideanMetric()
        self.root: KDTree.Node = self._init_tree(states, 0)

    def _init_tree(self, states: List[State], cdim: int) -> Node:
        if not states:
            return None
        if len(states) == 1:
            return KDTree.KDNode(states[0])
        
        ndim = (cdim+1) % self.dim

        m = (len(states)-1) // 2
        self._median(states, cdim)
        ret = KDTree.KDNode(states[m])
        ret.left = self._init_tree(states[:m], ndim)
        ret.right = self._init_tree(states[m+1:], ndim)
        return ret
    
    def metric(self) -> Metric:
        return self._metric
    
    def _median(self, states: List[State], dim: int):
        def _less(x: State, y: State) -> bool:
            return x[dim] < y[dim]
        m = (len(states)-1) // 2
        quickselect(states, m, _less)

    def insert(self, p: State):
        self.root = self._insert(self.root, p, 0)

    def _insert(self, node: Node, val: State, cd: int) -> Node:
        if node is None:
            return KDTree.KDNode(val)
        elif val == node.val:
            pass
        else:
            if val[cd] < node.val[cd]:
                node.left = self._insert(node.left, val, (cd+1) % self.dim)
            else:
                node.right = self._insert(node.right, val, (cd+1) % self.dim)
        return node

    def delete(self, p: State):
        self.root = self._delete(self.root, p, 0)

    def _delete(self, node: Node, val: State, cd: int):
        if node is not None:
            ncd = (cd+1) % self.dim

            if val == node.val:
                if node.right is not None:
                    node.val = self._find_min(node.right, cd, ncd)
                    node.right = self._delete(node.right, node.val, ncd)

                elif node.left is not None:
                    node.val = self._find_min(node.left, cd, ncd)
                    node.right = self._delete(node.left, node.val, ncd)
                else:
                    node = None
            elif val[cd] < node.val[cd]:
                node.left = self._delete(node.left, val, ncd)
            else:
                node.right = self._delete(node.right, val, ncd)
        return node

    def _find_min(self, node: Node, dim: int, cd: int) -> State:
        if node is None:
            return self.inf
        
        ncd = (cd+1) % self.dim
        if cd == dim:
            if node.left is None:
                return node.val
            else:
                return self._find_min(node.left, dim, ncd)
        else:
            return min(
                self._find_min(node.left, dim, ncd),
                self._find_min(node.right, dim, ncd),
                node.val
            )

    Heap = List[Tuple[float, State]]
    def nearest(self, p: State, k: int) -> Sequence[State]:
        # heapq реализует min-кучи, выталкивающие минимальное значение
        # поэтому будем хранить расстояния со знаками минус
        ret = [(-inf, self.inf) for _ in range(k)]
        # Todo: Логика поиска ближайших
        self._nearest(ret, self.root, p, 0)
        return [r[1] for r in ret]

    def _nearest(self, h: Heap, node: Node, p: State, cd: int):
        if node is not None:
            ncd = (cd+1) % self.dim
            # пробуем разместить вершину в куче
            # а затем вытолкнуть наибольшую из кучи
            if node.val != p:
                heap.heappushpop(h, (-self._metric(p, node.val), node.val))
            # длина перпендикуляра к плоскости
            cddiff = p[cd] - node.val[cd]
            # если длина отрицательная то искать сначала в левом (типа целевая точка находится слева
            # от рассматриваемой)
            # иначе в правом
            better, worse = (node.left, node.right) if cddiff < 0.0 else (node.right, node.left)
            self._nearest(h, better, p, ncd)
            # если перпендикуляр от целевой до плоскости меньше наибольшего расстояния в куче
            # то имеет смысл посмотреть в другое поддерево 
            if abs(cddiff) < -h[0][0]:
                self._nearest(h, worse, p, ncd)
