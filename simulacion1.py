import networkx as nx
import numpy as np
import random
import os
from datetime import datetime
from difusion_lib import ControladorPelado, VisualizadorPelado

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

def cantidad_nodos_mojados(record):
    n=0
    for i in record:
        if i!=0:
            n=n+1
    return n
    
def ejecutar_estudio_completo():
    print("=== INICIANDO ESTUDIO DE SIMULACIONES CON MASTER DASHBOARD ===")
    
    marca_tiempo = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    carpeta_maestra = os.path.join("simulaciones", f"estudio_pelado_{marca_tiempo}")
    os.makedirs(carpeta_maestra, exist_ok=True)
    
    mega_recolector = {}

    # print("\n>>> Sim 1: Cascada Jerárquica...")
    # G1 = generar_cascada_estricta()
    # ctrl1 = ControladorPelado(G1)
    # _, figs1 = ctrl1.ejecutar_estudio_pelado(
    #     num_pelados=100, iteraciones_por_pelado=30, umbral_masa=1.1,
    #     exportar_resultados=True, carpeta_exportacion=os.path.join(carpeta_maestra, "sim1_cascada"),
    #     tasa_difusion=0.3
    # )
    # mega_recolector["1. Cascada"] = figs1

    # print("\n>>> Sim 2: Scale-Free...")
    # G2 = generar_flujo_libre_escala(n_nodos=1000)
    # ctrl2 = ControladorPelado(G2)
    # _, figs2 = ctrl2.ejecutar_estudio_pelado(
    #     num_pelados=100, iteraciones_por_pelado=20, umbral_masa=1.1,
    #     exportar_resultados=True, carpeta_exportacion=os.path.join(carpeta_maestra, "sim2_scalefree"),
    #     tasa_difusion=0.3
    # )
    # mega_recolector["2. Scale-Free"] = figs2

    # print("\n>>> Sim 3: Estocástico (SBM)...")
    # G3 = generar_sbm_estocastico(n_total=300, n_grupos=10)
    # ctrl3 = ControladorPelado(G3)
    # _, figs3 = ctrl3.ejecutar_estudio_pelado(
    #     num_pelados=100, iteraciones_por_pelado=15, umbral_masa=1.1,
    #     exportar_resultados=True, carpeta_exportacion=os.path.join(carpeta_maestra, "sim3_estocastico"),
    #     tasa_difusion=0.3
    # )
    # mega_recolector["3. Estocástico"] = figs3

    # print("\n>>> Sim 4: Distribución Gaussiana...")
    # G4, pesos_ini = generar_red_gaussiana(n_nodos=200)
    # ctrl4 = ControladorPelado(G4)
    # _, figs4 = ctrl4.ejecutar_estudio_pelado(
    #     num_pelados=100, iteraciones_por_pelado=100, umbral_masa=1.1,
    #     valor_inicio=pesos_ini, exportar_resultados=True,
    #     carpeta_exportacion=os.path.join(carpeta_maestra, "sim4_gaussiana"),
    #     tasa_difusion=0.5
    # )
    # mega_recolector["4. Gaussiana"] = figs4

    print("\n>>> Sim 5: Malla Estocástica (NetLogo)...")
    dim=10
    G5 = generar_malla_estocastica_netlogo(dim=int(dim), link_chance=50)

    ctrl5 = ControladorPelado(G5)
    _, figs5 ,G,resumen_nodos= ctrl5.ejecutar_estudio_pelado(
        num_pelados=30, iteraciones_por_pelado=200, umbral_masa=1.0,umbral_nodos_final=0.01*pow(dim,2),
        exportar_resultados=True, carpeta_exportacion=os.path.join(carpeta_maestra, "sim5_malla_netlogo"),
        tasa_difusion=0.4
    )
    mega_recolector["5. Malla NetLogo"] = figs5
    print(resumen_nodos)
    
    ctrl5 = ControladorPelado(G5)
    _, figs6,record_final= ctrl5.ejecutar_estudio(iteraciones=1000,nodos=G.nodes,tasa_difusion=0.4,valor_inicio=pow(dim,2),
                                                  exportar_resultados=True,nombre_resumen='Final',carpeta_exportacion=os.path.join(carpeta_maestra, "sim5_malla_netlogo/DifusionFinal"))
    mega_recolector['5. Final Netlogo Difusin']=figs6
    
    
    
    metricas=[]
    # metricas.append(,cantidad_nodos_mojados(record_final))
    # print(metricas)
    # for i in range(len(G5.nodes)):
    #     _, figs_nodo,record = ctrl5.ejecutar_estudio(iteraciones=10,
    #                                              nodos=[i],tasa_difusion=0.4,valor_inicio=144,
    #                                              exportar_resultados=True,nombre_resumen=f"Difusión para nodo : {i}",
    #                                              carpeta_exportacion=os.path.join(carpeta_maestra, f"sim5_malla_netlogo/Difusion_Nodo_{i}"))
    #     mega_recolector[f"Final Netlogo Nodo {i}"]=figs_nodo
    #     metricas.append(cantidad_nodos_mojados(record))
    print(metricas)
    print(cantidad_nodos_mojados(record_final))
    print("\n" + "="*50)
    print("CONSOLIDANDO MASTER DASHBOARD (2 NIVELES)...")
    VisualizadorPelado.exportar_mega_dashboard(
        mega_recolector,
        carpeta_maestra, 
        "panel_control_total.html"
    )
    print(f"BATERÍA COMPLETADA EXITOSAMENTE")
    print(f"Panel Interactivo: {os.path.join(carpeta_maestra, 'panel_control_total.html')}")
    print("="*50)

if __name__ == "__main__":
    ejecutar_estudio_completo()