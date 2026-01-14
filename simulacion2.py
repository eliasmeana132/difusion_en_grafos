import networkx as nx
import numpy as np
import random
import os
import gzip
from datetime import datetime
from difusion_lib import ControladorPelado, VisualizadorPelado

def generar_red_facebook(file_path='facebook_combined.txt.gz'):
    """
    Carga el dataset real de Facebook y lo prepara para la simulación.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No se encontró el archivo: {file_path}")

    print(f"--- Cargando dataset de Facebook ({file_path}) ---")
    
    with gzip.open(file_path, 'rb') as f:
        G = nx.read_edgelist(f, create_using=nx.DiGraph(), nodetype=int)
    
    for n in G.nodes():
        G.nodes[n]['val'] = 1.0
        
    print(f"Grafo cargado exitosamente: {G.number_of_nodes()} nodos y {G.number_of_edges()} aristas.")
    return G

def ejecutar_simulacion_facebook():
    print("=== INICIANDO SIMULACIÓN: DATASET FACEBOOK REAL-WORLD ===")

    marca_tiempo = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    carpeta_maestra = os.path.join("simulaciones", f"estudio_facebook_{marca_tiempo}")
    os.makedirs(carpeta_maestra, exist_ok=True)
    
    mega_recolector = {}

    try:
        G = generar_red_facebook('cit-HepPh.txt.gz')
    except Exception as e:
        print(f"ERROR: {e}")
        return


    ctrl = ControladorPelado(G)

    print("\n>>> Ejecutando estudio de difusión en red de Facebook...")
    resultados, figs = ctrl.ejecutar_estudio_pelado(
        num_pelados=10,             
        iteraciones_por_pelado=1,  
        umbral_masa=1.5,           
        exportar_resultados=True, 
        carpeta_exportacion=os.path.join(carpeta_maestra, "sim_facebook_raw"),
        tasa_difusion=0.8          
    )
    mega_recolector["6. Facebook Real Net"] = figs

  
    print("\n" + "="*50)
    print("GENERANDO DASHBOARD FINAL...")
    VisualizadorPelado.exportar_mega_dashboard(
        mega_recolector,
        carpeta_maestra, 
        "dashboard_facebook.html"
    )
    
    print(f"PROCESO FINALIZADO")
    print(f"Resultados en: {carpeta_maestra}")
    print(f"Panel Interactivo: {os.path.join(carpeta_maestra, 'dashboard_facebook.html')}")
    print("="*50)

if __name__ == "__main__":
    ejecutar_simulacion_facebook()