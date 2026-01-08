import networkx as nx
import numpy as np
import random
import os
from datetime import datetime
from difusion_lib import ControladorPelado

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
    return G, distribucion_inicial

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

def ejecutar_estudio_completo():
    print("=== INICIANDO ESTUDIO DE SIMULACIONES ===")
    
    marca_tiempo = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    carpeta_maestra = os.path.join("simulaciones", f"estudio_pelado_{marca_tiempo}")
    os.makedirs(carpeta_maestra, exist_ok=True)
    print(f"Resultados de esta sesión en: {carpeta_maestra}\n")

    print(">>> Ejecutando Simulacion 1: Cascada Jerárquica...")
    G1 = generar_cascada_estricta()
    ctrl1 = ControladorPelado(G1)
    ctrl1.ejecutar_estudio_pelado(
        num_pelados=10,
        iteraciones_por_pelado=30,
        umbral_masa=1.1,
        exportar_resultados=True,
        carpeta_exportacion=os.path.join(carpeta_maestra, "simulacion1_cascada"),
        tasa_difusion=0.3
    )

    print("\n>>> Ejecutando Simulacion 2: Scale-Free ...")
    G2 = generar_flujo_libre_escala(n_nodos=1000)
    ctrl2 = ControladorPelado(G2)
    ctrl2.ejecutar_estudio_pelado(
        num_pelados=10,
        iteraciones_por_pelado=20,
        umbral_masa=1.1,
        exportar_resultados=True,
        carpeta_exportacion=os.path.join(carpeta_maestra, "simulacion2_scalefree"),
        tasa_difusion=0.3
    )

    print("\n>>> Ejecutando Simulacion 3: Estocástico  ...")
    G3 = generar_sbm_estocastico(n_total=300, n_grupos=10)
    ctrl3 = ControladorPelado(G3)
    ctrl3.ejecutar_estudio_pelado(
        num_pelados=20,
        iteraciones_por_pelado=15,
        umbral_masa=1.1,
        exportar_resultados=True,
        carpeta_exportacion=os.path.join(carpeta_maestra, "simulacion3_estocastico"),
        tasa_difusion=0.3
    )

    print("\n>>> Ejecutando Simulacion 4: Distribución Gaussiana Inicial...")
    G4, pesos_ini = generar_red_gaussiana(n_nodos=200)
    ctrl4 = ControladorPelado(G4)
    ctrl4.ejecutar_estudio_pelado(
        num_pelados=20,
        iteraciones_por_pelado=100,
        umbral_masa=1.1,
        valor_inicio=pesos_ini,
        exportar_resultados=True,
        carpeta_exportacion=os.path.join(carpeta_maestra, "simulacion4_gaussiana"),
        tasa_difusion=0.5
    )

    print("\n>>> Ejecutando Simulacion 5: Malla Estocástica (Estilo NetLogo)...")
    G5 = generar_malla_estocastica_netlogo(dim=30, link_chance=20)
    ctrl5 = ControladorPelado(G5)
    ctrl5.ejecutar_estudio_pelado(
        mostrar_graficos=False,
        num_pelados=20,
        iteraciones_por_pelado=200,
        umbral_masa=1.1,
        exportar_resultados=True,
        carpeta_exportacion=os.path.join(carpeta_maestra, "simulacion5_malla_netlogo"),
        tasa_difusion=0.4
    )
    
    print("\n" + "="*50)
    print(f"BATERÍA COMPLETADA EXITOSAMENTE")
    print(f"Ubicación: {carpeta_maestra}")
    print("="*50)

if __name__ == "__main__":
    ejecutar_estudio_completo()