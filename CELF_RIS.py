
import matplotlib.pyplot as plt
import random
import numpy as np
import time
from igraph import *
import pandas as pd
from collections import Counter
import os
import networkx as nx
from difusion_lib import ControladorPelado, VisualizadorPelado, GeneradorRedes

def generar_malla_estocastica_igraph(dim=30, link_chance=40):
    n_total = dim * dim
    g = Graph(directed=True)
    g.add_vertices(n_total)
    g.vs["val"] = 1.0
    
    edges_to_add = []
    
    for r in range(dim):
        for c in range(dim):
            nodo_actual = r * dim + c
            targets = []

            # Lógica de vecinos (idéntica a tu código original)
            if r > 0: targets.append((r - 1) * dim + c)       # Arriba
            if r < dim - 1: targets.append((r + 1) * dim + c) # Abajo
            if c > 0: targets.append(r * dim + (c - 1))       # Izquierda
            if c < dim - 1: targets.append(r * dim + (c + 1)) # Derecha
            
            for t in targets:
                if random.random() * 100 < link_chance:
                    edges_to_add.append((nodo_actual, t))
    
    # 4. Añadir todos los enlaces de golpe
    g.add_edges(edges_to_add)
    
    return g

def get_RRS(G,p):   
    """
    Inputs: G:  Ex2 dataframe of directed edges. Columns: ['source','target']
            p:  Disease propagation probability
    Return: A random reverse reachable set expressed as a list of nodes
    """
    
    # Step 1. Select random source node
    source = random.choice(np.unique(G['source']))
    
    # Step 2. Get an instance of g from G by sampling edges  
    g = G.copy().loc[np.random.uniform(0,1,G.shape[0]) < p]

    # Step 3. Construct reverse reachable set of the random source node
    new_nodes, RRS0 = [source], [source]   
    while new_nodes:
        
        # Limit to edges that flow into the source node
        temp = g.loc[g['target'].isin(new_nodes)]

        # Extract the nodes flowing into the source node
        temp = temp['source'].tolist()

        # Add new set of in-neighbors to the RRS
        RRS = list(set(RRS0 + temp))

        # Find what new nodes were added
        new_nodes = list(set(RRS) - set(RRS0))

        # Reset loop variables
        RRS0 = RRS[:]

    return(RRS)

def ris(G,k,p=0.5,mc=1000):    
    """
    Inputs: G:  Ex2 dataframe of directed edges. Columns: ['source','target']
            k:  Size of seed set
            p:  Disease propagation probability
            mc: Number of RRSs to generate
    Return: A seed set of nodes as an approximate solution to the IM problem
    """
    
    # Step 1. Generate the collection of random RRSs
    start_time = time.time()
    R = [get_RRS(G,p) for _ in range(mc)]

    # Step 2. Choose nodes that appear most often (maximum coverage greedy algorithm)
    SEED, timelapse = [], []
    for _ in range(k):
        
        # Find node that occurs most often in R and add to seed set
        flat_list = [item for sublist in R for item in sublist]
        seed = Counter(flat_list).most_common()[0][0]
        SEED.append(seed)
        
        # Remove RRSs containing last chosen seed 
        R = [rrs for rrs in R if seed not in rrs]
        
        # Record Time
        timelapse.append(time.time() - start_time)
    
    return(sorted(SEED),timelapse)


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

# G = Graph.Erdos_Renyi(n=1000,m=1500,directed=True)
G = generar_malla_estocastica_igraph(1000,link_chance=60)
A=nx.DiGraph(G.get_edgelist())
B=A.copy()

# Estudio Nuestro
ctrl_peel = ControladorPelado(A)
folder_sim = os.path.join('simulaciones', '0')

start_time_nuestro=time.time()
_, figs_peel, G_survivors, pelados_dict = ctrl_peel.ejecutar_estudio_pelado(
        generar_visualizaciones=False,
        mostrar_graficos=False,
        num_pelados=200,
        iteraciones_por_pelado=10,
        umbral_masa=1.0,
        umbral_nodos_final=1, 
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
            generar_visualizaciones=False
        )
n_mojados_nuestro = cantidad_nodos_mojados(record_final)

print(f"Nuestro: {n_mojados_nuestro}")
print(f"Nuestros nodos: {G_survivors.nodes()} En {end_time_nuestro-start_time_nuestro} segundos")


# Estudio de celf
# start_time_celf=time.time()
# celf_output   = celf(G,2,p = 0.2,mc = 1000)
# end_time_celf=time.time()

# ctrl_diff_celf = ControladorPelado(B)
# folder_diff_celf = os.path.join(folder_sim, "Difusion_Core_CELF")
# _, figs_diff_celf, record_final_celf = ctrl_diff_celf.ejecutar_estudio(
#             iteraciones=100,
#             nodos=list(celf_output)[0], 
#             tasa_difusion=0.4,
#             valor_inicio=50,             
#             exportar_resultados=True,
#             carpeta_exportacion=folder_diff_celf,
#             nombre_resumen="resumen_difusion_final.csv",
#             generar_visualizaciones=True
#         )
# n_mojados_celf = cantidad_nodos_mojados(record_final_celf)


# Estudio RIS
source_nodes = [edge.source for edge in G.es]
target_nodes = [edge.target for edge in G.es]
df = pd.DataFrame({'source': source_nodes,'target': target_nodes})

start_time_ris=time.time()
ris_output  = ris(df,len(list(G_survivors.nodes())),p=0.5,mc=1000)
end_time_ris=time.time()

ctrl_diff_ris = ControladorPelado(B)
folder_diff_ris = os.path.join(folder_sim, "Difusion_Core_ris")
_, figs_diff_ris, record_final_ris = ctrl_diff_ris.ejecutar_estudio(
            iteraciones=100,
            nodos=list(ris_output)[0], 
            tasa_difusion=0.4,
            valor_inicio=50,             
            exportar_resultados=True,
            carpeta_exportacion=folder_diff_ris,
            nombre_resumen="resumen_difusion_final.csv",
            generar_visualizaciones=False
        )
n_mojados_ris = cantidad_nodos_mojados(record_final_ris)


# print(f"CELF: {n_mojados_celf}")
# print(f"celf output: {str(celf_output[0])} En {end_time_celf-start_time_celf} segundos")

print(f"RIS: {n_mojados_ris}")
print(f"RIS output: {str(ris_output[0])} En {end_time_ris-start_time_ris} segundos")


