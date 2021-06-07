from math import inf


class KDTree:
    class KDNode:
        def __init__(self, val):
            self.val = val
            self.left = self.right = None
    
    def __init__(self, dim, metric):
        self.dim = dim
        self.inf = tuple(inf for i in range(dim))
        self.metric = metric
        self.root = None

    def insert(self, val):
        self.root = self._insert(self.root, val, 0)

    def _insert(self, node, val, cd):
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

    def delete(self, val):
        self.root = self._delete(self.root, val, 0)

    def _delete(self, node, val, cd):
        if node is None:
            return node

        ncd = (cd+1) % self.dim

        if val == node.val:
            if node.right is not None:
                node.val = self._find_min(node.right, cd, ncd)
                node.right = self._delete(node.right, node.val, ncd)

            elif node.left is not None:
                node.val = self._find_min(node.left, cd, ncd)
                node.right = self._delete(node.left, node.val, ncd)

            else:
                return None

        elif val[cd] < node.val[cd]:
            node.left = self._delete(node.left, val, ncd)
        else:
            node.right = self._delete(node.right, val, ncd)

        return node

    def _find_min(self, node, dim, cd):
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

    def nearest(self, p, k):
        ret = [self.inf for i in range(k)]

        self._nearest(self.root, p, 0, ret)
        return ret
