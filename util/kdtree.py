# from __future__ import annotations
from math import inf
from typing import Optional, Sequence
from env.types import State
from graphs.prm.metrics import Metric


class KDTree:
    
    class KDNode:
        def __init__(self, val: State):
            self.val: State = val
            self.left: Optional[KDTree.KDNode] = None
            self.right: Optional[KDTree.KDNode] = None
    Node = Optional[KDNode]

    def __init__(self, dim: int, metric: Metric):
        self.dim = dim
        self.inf = tuple(inf for _ in range(dim))
        self.metric = metric
        self.root: KDTree.Node = None

    def insert(self, val: State):
        self.root = self._insert(self.root, val, 0)

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

    def delete(self, val: State):
        self.root = self._delete(self.root, val, 0)

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

    def nearest(self, p: State, k: int) -> Sequence[State]:
        ret = [self.inf for _ in range(k)]
        # Todo: Логика поиска ближайших
        return ret
