
import matplotlib.pyplot as plt
from random import uniform, seed
import numpy as np
import time
from igraph import *
import os
import networkx as nx
from difusion_lib import ControladorPelado, VisualizadorPelado, GeneradorRedes

def IC(g,S,p=0.5,mc=1000):
    """
    Input:  graph object, set of seed nodes, propagation probability
            and the number of Monte-Carlo simulations
    Output: average number of nodes influenced by the seed nodes
    """
    
    # Loop over the Monte-Carlo Simulations
    spread = []
    for i in range(mc):
        
        # Simulate propagation process      
        new_active, A = S[:], S[:]
        while new_active:

            # For each newly active node, find its neighbors that become activated
            new_ones = []
            for node in new_active:
                
                # Determine neighbors that become infected
                np.random.seed(i)
                success = np.random.uniform(0,1,len(g.neighbors(node,mode="out"))) < p
                new_ones += list(np.extract(success, g.neighbors(node,mode="out")))

            new_active = list(set(new_ones) - set(A))
            
            # Add newly activated nodes to the set of activated nodes
            A += new_active
            
        spread.append(len(A))
        
    return(np.mean(spread))

def celf(g,k,p=0.1,mc=1000):  
      
    # --------------------
    # Find the first node with greedy algorithm
    # --------------------
    
    # Calculate the first iteration sorted list
    start_time = time.time() 
    marg_gain = [IC(g,[node],p,mc) for node in range(g.vcount())]

    # Create the sorted list of nodes and their marginal gain 
    Q = sorted(zip(range(g.vcount()),marg_gain), key=lambda x: x[1],reverse=True)

    # Select the first node and remove from candidate list
    S, spread, SPREAD = [Q[0][0]], Q[0][1], [Q[0][1]]
    Q, LOOKUPS, timelapse = Q[1:], [g.vcount()], [time.time()-start_time]
    
    # --------------------
    # Find the next k-1 nodes using the list-sorting procedure
    # --------------------
    
    for _ in range(k-1):    

        check, node_lookup = False, 0
        
        while not check:
            
            # Count the number of times the spread is computed
            node_lookup += 1
            
            # Recalculate spread of top node
            current = Q[0][0]
            
            # Evaluate the spread function and store the marginal gain in the list
            Q[0] = (current,IC(g,S+[current],p,mc) - spread)

            # Re-sort the list
            Q = sorted(Q, key = lambda x: x[1], reverse = True)

            # Check if previous top node stayed on top after the sort
            check = (Q[0][0] == current)

        # Select the next node
        spread += Q[0][1]
        S.append(Q[0][0])
        SPREAD.append(spread)
        LOOKUPS.append(node_lookup)
        timelapse.append(time.time() - start_time)

        # Remove the selected node from the list
        Q = Q[1:]

    return(S,SPREAD,timelapse,LOOKUPS)



def cantidad_nodos_mojados(record):
    return sum(1 for i in record if i > 0)

G = Graph.Erdos_Renyi(n=100,m=150,directed=True)
A=nx.DiGraph(G.get_edgelist())
B=A.copy()

ctrl_peel = ControladorPelado(A)
folder_sim = os.path.join('simulaciones', '0')

start_time_nuestro=time.time()
_, figs_peel, G_survivors, pelados_dict = ctrl_peel.ejecutar_estudio_pelado(
        generar_visualizaciones=False,
        mostrar_graficos=False,
        num_pelados=200,
        iteraciones_por_pelado=100,
        umbral_masa=1.0,
        umbral_nodos_final=2, 
        tasa_difusion=0.4,
        exportar_resultados=True,
        carpeta_exportacion=os.path.join('simulaciones', '0-nuestro'),
        cfc=False)
end_time_nuestro=time.time()

ctrl_diff = ControladorPelado(A)
folder_diff = os.path.join(folder_sim, "Difusion_Core")

print(list(G_survivors.nodes()))
_, figs_diff, record_final = ctrl_diff.ejecutar_estudio(
            iteraciones=100,
            nodos=list(G_survivors.nodes()), 
            tasa_difusion=0.4,
            valor_inicio=50,             
            exportar_resultados=True,
            carpeta_exportacion=folder_diff,
            nombre_resumen="resumen_difusion_final.csv",
            generar_visualizaciones=True
        )
n_mojados_nuestro = cantidad_nodos_mojados(record_final)

print(f"Nuestro: {n_mojados_nuestro}")
print(f"Nuestros nodos: {G_survivors.nodes()} En {end_time_nuestro-start_time_nuestro} segundos")

start_time_celf=time.time()
celf_output   = celf(G,2,p = 0.2,mc = 1000)
end_time_celf=time.time()

ctrl_diff_celf = ControladorPelado(B)
folder_diff_celf = os.path.join(folder_sim, "Difusion_Core_CELF")
_, figs_diff_celf, record_final_celf = ctrl_diff_celf.ejecutar_estudio(
            iteraciones=100,
            nodos=list(celf_output)[0], 
            tasa_difusion=0.4,
            valor_inicio=50,             
            exportar_resultados=True,
            carpeta_exportacion=folder_diff_celf,
            nombre_resumen="resumen_difusion_final.csv",
            generar_visualizaciones=True
        )

n_mojados_celf = cantidad_nodos_mojados(record_final_celf)


print(f"CELF: {n_mojados_celf}")
print(f"celf output: {str(celf_output[0])} En {end_time_celf-start_time_celf} segundos")



# @staticmethod
# def generar_malla_estocastica_igraph(dim=3, link_chance=40):
#     n_total = dim * dim
    
#     g = ig.Graph(directed=True)
#     g.add_vertices(n_total)
    

#     g.vs["val"] = 1.0
    
#     edges_to_add = []
    
#     for r in range(dim):
#         for c in range(dim):
#             nodo_actual = r * dim + c
#             targets = []

#             if r > 0: targets.append((r - 1) * dim + c)       # Arriba
#             if r < dim - 1: targets.append((r + 1) * dim + c) # Abajo
#             if c > 0: targets.append(r * dim + (c - 1))       # Izquierda
#             if c < dim - 1: targets.append(r * dim + (c + 1)) # Derecha
            
#             for t in targets:
#                 if random.random() * 100 < link_chance:
#                     edges_to_add.append((nodo_actual, t))
    
#     # 4. Añadir todos los enlaces de golpe
#     g.add_edges(edges_to_add)
    
#     return g
