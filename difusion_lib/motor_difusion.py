import networkx as nx
import numpy as np
from scipy import sparse

class MotorDifusion:
    def __init__(self, G, tasa_difusion=0.7):
        self.G = G
        self.tasa_difusion = tasa_difusion
        self._nodes = list(G.nodes())
        self._num_nodes = len(self._nodes)
        self._M = self._preparar_matriz()

    def _preparar_matriz(self):
        if self._num_nodes == 0:
            return None
        A = nx.to_scipy_sparse_array(self.G, nodelist=self._nodes, format='csr').T
        out_degrees = np.array(A.sum(axis=0)).flatten()
        with np.errstate(divide='ignore'):
            weights = self.tasa_difusion / out_degrees
        weights[np.isinf(weights)] = 0  
        M = A.dot(sparse.diags(weights))
        diag_values = np.where(out_degrees > 0, 1 - self.tasa_difusion, 1.0)
        M += sparse.diags(diag_values)
        return M.tocsr()

    def ejecutar(self, iteraciones=100):
        if self._M is None:
            return
        v = np.array([self.G.nodes[n].get('val', 0.0) for n in self._nodes])
        for _ in range(iteraciones):
            v = self._M.dot(v)
        for i, n in enumerate(self._nodes):
            self.G.nodes[n]['val'] = v[i]