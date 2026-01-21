import networkx as nx
import random
import numpy as np
import time
from igraph import *
import pandas as pd
from collections import Counter
import networkx as nx

class AnalizadorPelado:
    @staticmethod
    def obtener_metricas_cfc(G, version_pelado, total_nodos_original):
        if G.is_directed():
            componentes = list(nx.strongly_connected_components(G))
        else:
            componentes = list(nx.connected_components(G))
        resultados = []
        for i, nodos in enumerate(componentes):
            masa = sum(G.nodes[n]['val'] for n in nodos)
            es_trivial = len(nodos) == 1 and not G.has_edge(list(nodos)[0], list(nodos)[0])
            resultados.append({
                'capa_pelado': version_pelado + 1,
                'id_componente': f"P{version_pelado+1}_C{i}",
                'nodos': sorted(list(nodos)),
                'tamano': len(nodos),
                'es_trivial': es_trivial,
                'masa_total': masa,
                'impacto_global': masa / total_nodos_original if total_nodos_original > 0 else 0
            })
        return sorted(resultados, key=lambda x: x['masa_total'], reverse=True)
    
    @staticmethod
    def nodos_para_quitar(G, version_pelado, total_nodos_original, umbral_masa=1.0):
        resultados = []
        
        nodos_filtrados = [n for n, attr in G.nodes(data=True) if attr.get('val', 0) >= umbral_masa]
        
        if not nodos_filtrados:
            return []

        for nodo in nodos_filtrados:
            masa_nodo = G.nodes[nodo]['val']
            resultados.append({
                'capa_pelado': version_pelado + 1,
                'id_componente': f"P{version_pelado+1}_N{nodo}", 
                'nodos': [nodo], 
                'masa_total': masa_nodo
            })
            
        return sorted(resultados, key=lambda x: x['masa_total'], reverse=True)

class AnalizadorRIS:
    @staticmethod
    def get_RRS(G, p):   
        source = random.choice(np.unique(G['source']))
        # nodes = np.unique(np.concatenate([G['source'], G['target']]))
        # source = random.choice(nodes)
        g = G.copy().loc[np.random.uniform(0, 1, G.shape[0]) < p]
        
        new_nodes, RRS0 = [source], [source]   
        while new_nodes:
            temp = g.loc[g['target'].isin(new_nodes)]
            temp = temp['source'].tolist()
            
            RRS = list(set(RRS0 + temp))
            new_nodes = list(set(RRS) - set(RRS0))
            RRS0 = RRS[:]
        return RRS

    @staticmethod
    def ris(G, k, p=0.5, mc=1000):    
        start_time = time.time()
        R = [AnalizadorRIS.get_RRS(G, p) for _ in range(mc)]
        
        SEED, timelapse = [], []
        for _ in range(k):
            
            flat_list = [item for sublist in R for item in sublist]
            if not flat_list: 
                break
                
            seed = Counter(flat_list).most_common()[0][0]
            SEED.append(seed)
            R = [rrs for rrs in R if seed not in rrs]
            timelapse.append(time.time() - start_time)
            
        return sorted(SEED), timelapse

class AnalizadorCELF:
    @staticmethod
    def IC(g, S, p=0.5, mc=1000):
        spread = []
        for i in range(mc):
            new_active, A = list(S), list(S)
            while new_active:
                new_ones = []
                for node in new_active:
                    neighbors = g.neighbors(node, mode="out")
                    if not neighbors:
                        continue
                    success = np.random.uniform(0, 1, len(neighbors)) < p
                    new_ones += [neighbors[j] for j, is_success in enumerate(success) if is_success]
                new_active = list(set(new_ones) - set(A))
                A += new_active
            spread.append(len(A))
        return np.mean(spread)

    @staticmethod
    def ejecutar_celf(g, k, p=0.1, mc=1000):
        start_time = time.time()
        # print(f"CELF: Calculando ganancia marginal inicial para {g.vcount()} nodos...")
        marg_gain = [AnalizadorCELF.IC(g, [node], p, mc) for node in range(g.vcount())]
        Q = sorted(zip(range(g.vcount()), marg_gain), key=lambda x: x[1], reverse=True)
        S = [Q[0][0]]
        spread = Q[0][1]
        SPREAD = [spread]
        Q = Q[1:] 
        
        LOOKUPS = [g.vcount()]
        timelapse = [time.time() - start_time]
        for i in range(k - 1):
            check = False
            node_lookup = 0
            
            while not check:
                node_lookup += 1
                current_node = Q[0][0]
            
                nueva_ganancia = AnalizadorCELF.IC(g, S + [current_node], p, mc) - spread

                Q[0] = (current_node, nueva_ganancia)
                Q = sorted(Q, key=lambda x: x[1], reverse=True)
                check = (Q[0][0] == current_node)

            spread += Q[0][1]
            S.append(Q[0][0])
            SPREAD.append(spread)
            LOOKUPS.append(node_lookup)
            timelapse.append(time.time() - start_time)
            Q = Q[1:]
            # print(f"Semilla {i+2} seleccionada: {S[-1]} | Spread total: {spread:.2f}")

        return S, SPREAD, timelapse, LOOKUPS