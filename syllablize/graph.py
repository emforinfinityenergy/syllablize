from typing import *
import numpy as np


class AdjacencyMatrix:
    def __init__(self, n: int, m: int):
        self.matrix: np.ndarray[bool] = np.full([n, m], False)
        self.o_deg: np.ndarray[int] = np.zeros([n])

    def connect(self, u: int, v: int) -> None:
        self.matrix[u][v] = True
        self.o_deg[u] += 1

    def disconnect(self, u: int, v: int) -> None:
        self.matrix[u][v] = False
        self.o_deg[u] -= 1

    def __getitem__(self, n: int) -> np.ndarray[bool]:
        return self.matrix[n]


class ChainForwardStar:
    def __init__(self, m: int):
        self.head: np.ndarray[int] = np.full([m + 5], -1)
        self.next: np.ndarray[int] = np.full([m + 5], -1)
        self.to: np.ndarray[int] = np.full([m + 5], -1)
        self.cnt = 0

    def connect(self, u: int, v: int):
        self.cnt += 1
        self.next[self.cnt] = self.head[u]
        self.head[u] = self.cnt
        self.to[self.cnt] = v


class ChainForwardStarIterator(Iterator):
    def __init__(self, graph: ChainForwardStar, u: int):
        self.graph = graph
        self.u = u
        self.i = self.graph.head[u]

    def __next__(self):
        if self.i == -1:
            raise StopIteration
        ret = self.graph.to[self.i]
        self.i = self.graph.next[self.i]
        return ret
