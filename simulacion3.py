import networkx as nx
import numpy as np
import random
import os
from datetime import datetime
from difusion_lib import ControladorPelado, VisualizadorPelado

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
    print("=== INICIANDO ESTUDIO DE SIMULACIONES CON MASTER DASHBOARD ===")
    
    marca_tiempo = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    carpeta_maestra = os.path.join("simulaciones", f"estudio_pelado_{marca_tiempo}")
    os.makedirs(carpeta_maestra, exist_ok=True)
    
    mega_recolector = {}
    
    umbral_masa_inicial = 1.0
    iteraciones = 2000
    
    print("\n>>> Generando Malla Estocástica (NetLogo)...")
    G_base = generar_malla_estocastica_netlogo(dim=3, link_chance=60)

    print("\n>>> Sim 5: Ejecutando con método DIFUSIÓN...")
    ruta_sim5 = os.path.join(carpeta_maestra, "sim5_malla_difusion") # Carpeta propia
    ctrl5 = ControladorPelado(G_base)
    _, figs5 = ctrl5.ejecutar_estudio_pelado(
        num_pelados=10, 
        iteraciones_por_pelado=iteraciones, 
        umbral_masa=umbral_masa_inicial,
        valor_inicio=1.0,
        exportar_resultados=True, 
        carpeta_exportacion=ruta_sim5,
        tasa_difusion=0.4,
        metodo_deteccion='difusion'
    )
    mega_recolector["5. Malla NetLogo (Difusión)"] = figs5
    
    print("\n>>> Sim 6: Ejecutando con método TARJAN...")
    ruta_sim6 = os.path.join(carpeta_maestra, "sim6_malla_tarjan") # Carpeta propia
    ctrl6 = ControladorPelado(G_base)
    _, figs6 = ctrl6.ejecutar_estudio_pelado(
        num_pelados=10, 
        iteraciones_por_pelado=iteraciones, 
        umbral_masa=umbral_masa_inicial,
        valor_inicio=1.0,
        exportar_resultados=True, 
        carpeta_exportacion=ruta_sim6,
        tasa_difusion=0.4,
        metodo_deteccion='tarjan'
    )
    mega_recolector["6. Malla NetLogo (Tarjan)"] = figs6

    print("\n" + "="*50)
    print("CONSOLIDANDO MASTER DASHBOARD (2 NIVELES)...")
    VisualizadorPelado.exportar_mega_dashboard(
        mega_recolector,
        carpeta_maestra, 
        "panel_control_total.html"
    )
    
    print(f"Resultados en: {carpeta_maestra}")
    print(f"Panel Interactivo: {os.path.join(carpeta_maestra, 'panel_control_total.html')}")
    print("="*50)

if __name__ == "__main__":
    ejecutar_estudio_completo()