import networkx as nx
import numpy as np
import random

class GeneradorRedes:
    @staticmethod
    def generar_cascada_estricta(n_bloques=100, nodos_por_bloque=4):
        G = nx.DiGraph()
        for b in range(n_bloques):
            nodo_inicio = b * nodos_por_bloque
            nodos = list(range(nodo_inicio, nodo_inicio + nodos_por_bloque))
            for i in range(len(nodos)):
                u = nodos[i]
                v = nodos[(i + 1) % len(nodos)]
                G.add_edge(u, v)
            for _ in range(nodos_por_bloque * 2):
                u = random.choice(nodos)
                v = random.choice(nodos)
                if u != v: G.add_edge(u, v)
            if b < n_bloques - 1:
                nodos_siguiente_bloque = list(range((b + 1) * nodos_por_bloque, (b + 2) * nodos_por_bloque))
                for _ in range(5):
                    u = random.choice(nodos)
                    v = random.choice(nodos_siguiente_bloque)
                    G.add_edge(u, v)
        for n in G.nodes():
            G.nodes[n]['val'] = 1.0
        return G

    @staticmethod
    def generar_flujo_libre_escala(n_nodos=1000):
        G_base = nx.barabasi_albert_graph(n_nodos, 2, seed=42)
        G = nx.DiGraph()
        for u, v in G_base.edges():
            if u < v: G.add_edge(u, v)
            else: G.add_edge(v, u)
        nodos = list(G.nodes())
        for _ in range(20):
            u = nodos[random.randint(50, n_nodos-1)]
            v = nodos[random.randint(0, 49)]
            G.add_edge(u, v)
        for n in G.nodes():
            G.nodes[n]['val'] = 1.0
        return G

    @staticmethod
    def generar_sbm_estocastico(n_total=300, n_grupos=10):
        tamanos = np.random.multinomial(n_total, [1/n_grupos]*n_grupos).tolist()
        probs = np.full((n_grupos, n_grupos), 0.001) 
        for i in range(n_grupos):
            probs[i][i] = 0.02 
            if i < n_grupos - 1:
                probs[i][i+1] = 0.01 
                
        G_base = nx.stochastic_block_model(tamanos, probs, directed=True, seed=42)
        G = nx.DiGraph(G_base)
        for n in G.nodes():
            G.nodes[n]['val'] = 1.0
        return G

    @staticmethod
    def generar_red_gaussiana(n_nodos=200, radius=0.10):
        G_base = nx.random_geometric_graph(n_nodos, radius)
        G = nx.DiGraph()
        for u, v in G_base.edges():
            if random.random() > 0.5:
                G.add_edge(u, v)
            else:
                G.add_edge(v, u)
                
        nodos = list(G.nodes())

        pesos_gaussianos = np.random.normal(loc=1.0, scale=0.3, size=len(nodos))
        pesos_gaussianos = np.clip(pesos_gaussianos, 0.1, None)
        
        distribucion_inicial = {nodos[i]: pesos_gaussianos[i] for i in range(len(nodos))}
        
        for n, val in distribucion_inicial.items():
            G.nodes[n]['val'] = val
            
        return G

    @staticmethod
    def generar_malla_estocastica_netlogo(dim=3, link_chance=40):
        G = nx.DiGraph()
        for r in range(dim):
            for c in range(dim):
                nodo_actual = r * dim + c
                G.add_node(nodo_actual, val=1.0)
                targets = []

                if r > 0: targets.append((r - 1) * dim + c)
                if r < dim - 1: targets.append((r + 1) * dim + c)
                if c > 0: targets.append(r * dim + (c - 1))
                if c < dim - 1: targets.append(r * dim + (c + 1))
                
                for t in targets:
                    if random.random() * 100 < link_chance:
                        G.add_edge(nodo_actual, t)
        return G
    
    @staticmethod
    def generar_red_social_realista(n_users=300, m_neighbors=2, p_triangle=0.3, ratio_mutual=0.05):
        G_base = nx.powerlaw_cluster_graph(n_users, m_neighbors, p_triangle, seed=42)
        
        G = nx.DiGraph()
        
        for u, v in G_base.edges():
            if random.random() < ratio_mutual:
                G.add_edge(u, v)
                G.add_edge(v, u)
            else:
                
                if random.random() < 0.5:
                    G.add_edge(u, v)
                else:
                    G.add_edge(v, u)
        
        for n in G.nodes():
            if random.random() < 0.20: 
                out_edges = list(G.out_edges(n))
                G.remove_edges_from(out_edges)
            
        return G