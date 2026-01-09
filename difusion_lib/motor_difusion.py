import networkx as nx

class MotorDifusion:
    def __init__(self, G, tasa_difusion=0.7):
        self.G = G
        self.tasa_difusion = tasa_difusion

    def ejecutar(self, iteraciones=100):
        es_dirigido = self.G.is_directed()
        for _ in range(iteraciones):
            actualizaciones = {n: 0.0 for n in self.G.nodes()}
            for n in self.G.nodes():
                valor = self.G.nodes[n]['val']
                vecinos = list(self.G.successors(n)) if es_dirigido else list(self.G.neighbors(n))
                if vecinos:
                    mantener = valor * (1 - self.tasa_difusion)
                    actualizaciones[n] += mantener
                    reparto = (valor - mantener) / len(vecinos)
                    for v in vecinos:
                        actualizaciones[v] += reparto
                else:
                    actualizaciones[n] += valor
            for n, v in actualizaciones.items():
                self.G.nodes[n]['val'] = v