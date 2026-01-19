import os
import pandas as pd
import networkx as nx
from datetime import datetime
from difusion_lib import ControladorPelado, VisualizadorPelado, GeneradorRedes
import time

def cantidad_nodos_mojados(record):
    """Cuenta cuántos nodos tienen un valor > 0 en el registro de difusión."""
    return sum(1 for i in record if i > 0)

def ejecutar_bateria_masiva(
    tipo_de_grafo='malla_netlogo', 
    n_simulaciones=5, 
    generar_visualizaciones=False,
    master_folder="simulaciones", 
    cfc=False,
    tasa_difusion=0.2, 
    num_pelados=10, 
    iteraciones_por_pelado=150, 
    iteraciones_difusion=150, 
    umbral_masa=1.0, 
    umbral_nodos_final=1, 
    masa_total_concentrada=100,
    **kwargs_grafo # 
):
    

    mapeo_generadores = {
        'malla_netlogo': GeneradorRedes.generar_malla_estocastica_netlogo,
        'cascada': GeneradorRedes.generar_cascada_estricta,
        'flujo_libre': GeneradorRedes.generar_flujo_libre_escala,
        'sbm': GeneradorRedes.generar_sbm_estocastico,
        'gaussiana': GeneradorRedes.generar_red_gaussiana,
        'red_social_realista' : GeneradorRedes.generar_red_social_realista
    }

    if tipo_de_grafo not in mapeo_generadores:
        raise ValueError(f"Grafo '{tipo_de_grafo}' no reconocido. Opciones: {list(mapeo_generadores.keys())}")

    if not os.path.exists(master_folder):
        os.makedirs(master_folder)
        print(f"Carpeta maestra creada: {master_folder}")

    mega_recolector_figs = {} 
    resumen_metricas = []     

    print(f"=== INICIANDO BATERÍA: {tipo_de_grafo.upper()} (N={n_simulaciones}) ===")
    print(f"Parámetros del grafo: {kwargs_grafo}")

    for i in range(n_simulaciones):
        sim_id = f"Simulacion_{i+1:03d}" 
        print(f"\n>>> Procesando: {sim_id}")

        func_generadora = mapeo_generadores[tipo_de_grafo]
        
        resultado_generador = func_generadora(**kwargs_grafo)

        if isinstance(resultado_generador, tuple):
            G_original = resultado_generador[0]
        else:
            G_original = resultado_generador

        n_total_nodos = len(G_original)

        ctrl_peel = ControladorPelado(G_original)
        folder_sim = os.path.join(master_folder, sim_id)
        
        start_time=time.time()
        _, figs_peel, G_survivors, pelados_dict = ctrl_peel.ejecutar_estudio_pelado(
            generar_visualizaciones=generar_visualizaciones,
            mostrar_graficos=False,
            num_pelados=num_pelados,
            iteraciones_por_pelado=iteraciones_por_pelado,
            umbral_masa=umbral_masa,
            umbral_nodos_final=umbral_nodos_final, 
            tasa_difusion=tasa_difusion,
            exportar_resultados=True,
            carpeta_exportacion=folder_sim,
            cfc=cfc)
        end_time=time.time()
        tiempo_eje= end_time-start_time
        
        num_peels = len(pelados_dict)
        if num_peels > 0:
            last_layer_idx = max(pelados_dict.keys())
            nodos_ultima_capa_eliminada = len(pelados_dict[last_layer_idx])
        else:
            nodos_ultima_capa_eliminada = 0
            
        nodos_sobrevivientes = len(G_survivors)

        ctrl_diff = ControladorPelado(G_original)
        folder_diff = os.path.join(folder_sim, "Difusion_Core")
        
        _, figs_diff, record_final = ctrl_diff.ejecutar_estudio(
            iteraciones=iteraciones_difusion,
            nodos=list(G_survivors.nodes()), 
            tasa_difusion=tasa_difusion,
            valor_inicio=masa_total_concentrada/len(list(G_survivors.nodes())),             
            exportar_resultados=True,
            carpeta_exportacion=folder_diff,
            nombre_resumen="resumen_difusion_final.csv",
            generar_visualizaciones=generar_visualizaciones
        )
        
        n_mojados = cantidad_nodos_mojados(record_final)
        
        ratio_val = float(n_mojados) / float(n_total_nodos) if n_total_nodos > 0 else 0.0

        mega_recolector_figs[f"{sim_id} - Pelado"] = figs_peel
        mega_recolector_figs[f"{sim_id} - Difusion"] = figs_diff
        
        resumen_metricas.append({
            "Simulacion_ID": sim_id,
            "Tipo_Grafo": tipo_de_grafo, 
            "Total_Nodos_Inicial": n_total_nodos,
            "Total_Capas_Peladas": num_peels,
            "Nodos_Ultima_Capa_Pelada": nodos_ultima_capa_eliminada,
            "Nodos_Sobrevivientes": nodos_sobrevivientes,
            "Nodos_Mojados": n_mojados,
            "Ratio_Mojados": ratio_val,
            "Tiempo_Eje_Estudio_Pelado": tiempo_eje
        })

        print(f"   -> Pelados: {num_peels} | Mojados: {n_mojados} | Ratio: {ratio_val:.4f}")

    print("\nGenerando archivos maestros...")

    df_maestro = pd.DataFrame(resumen_metricas)
    path_csv = os.path.join(master_folder, f"Metricas_Consolidadas{'_cfc' if cfc else ''}.csv")
    df_maestro.to_csv(path_csv, index=False)
    
    cols_numericas = [
        "Total_Nodos_Inicial", "Total_Capas_Peladas", 
        "Nodos_Ultima_Capa_Pelada", "Nodos_Sobrevivientes", 
        "Nodos_Mojados", "Ratio_Mojados","Tiempo_Eje_Estudio_Pelado"
    ]
    for col in cols_numericas: df_maestro[col] = pd.to_numeric(df_maestro[col])
    
    df_promedios = df_maestro[cols_numericas].mean().to_frame(name="Promedio").T
    path_avg = os.path.join(master_folder, f"Promedios_Consolidados{'_cfc' if cfc else ''}.csv")
    df_promedios.to_csv(path_avg, index=False)
    if generar_visualizaciones:
        VisualizadorPelado.exportar_mega_dashboard(
            mega_recolector_figs,
            master_folder,
            "Dashboard_Global_3D.html"
        )
    print("=== BATERÍA COMPLETADA ===")
    
if __name__ == "__main__":
    marca_tiempo = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dim=10
    n_sim=10
    # print("--- EJECUTANDO MALLA NETLOGO ---")
    # ejecutar_bateria_masiva(
    #     tipo_de_grafo='malla_netlogo', 
    #     n_simulaciones=n_sim, 
    #     generar_visualizaciones=False,
    #     master_folder=f"simulaciones/Estudio_Masivo_{marca_tiempo}/Estudio_NETLOGO", 
    #     tasa_difusion=0.4, 
    #     num_pelados=200, 
    #     iteraciones_por_pelado=1, 
    #     iteraciones_difusion=150, 
    #     umbral_masa=1.0, 
    #     umbral_nodos_final=max(1, int(0.01 * pow(dim,2))), 
    #     masa_total_concentrada=pow(dim,2),
    #     dim=dim,           
    #     link_chance=40    
    # )
    
    # ejecutar_bateria_masiva(
    #     tipo_de_grafo='malla_netlogo', 
    #     n_simulaciones=1, 
    #     generar_visualizaciones=False,
    #     master_folder=f"simulaciones/Estudio_Masivo_{marca_tiempo}/Estudio_NETLOGO", 
    #     tasa_difusion=0.4, 
    #     num_pelados=200, 
    #     cfc=True,
    #     iteraciones_por_pelado=10, 
    #     iteraciones_difusion=150, 
    #     umbral_masa=1.0, 
    #     umbral_nodos_final=max(1, int(0.01 * pow(dim,2))), 
    #     masa_total_concentrada=pow(dim,2),
    #     dim=dim,           
    #     link_chance=60    
    # )
    num_de_usuarios=30000
    # n_sim=1
    iteraciones_difusion=10
    ejecutar_bateria_masiva(
        tipo_de_grafo='red_social_realista', 
        n_simulaciones=n_sim, 
        master_folder=f"simulaciones/Estudio_Masivo_{marca_tiempo}/red_social_realista", 
        tasa_difusion=0.2, 
        num_pelados=10, 
        iteraciones_por_pelado=10, 
        iteraciones_difusion=iteraciones_difusion, 
        umbral_masa=1.0, 
        umbral_nodos_final=max(1, int(0.0001 * num_de_usuarios)), 
        masa_total_concentrada=num_de_usuarios,
        n_users=num_de_usuarios,
        m_neighbors=2,
        p_triangle=0.3, 
        ratio_mutual=0.5,
        generar_visualizaciones=False
    )
    # ejecutar_bateria_masiva(
    #     tipo_de_grafo='red_social_realista', 
    #     n_simulaciones=n_sim, 
    #     master_folder=f"simulaciones/Estudio_Masivo_{marca_tiempo}/red_social_realista", 
    #     tasa_difusion=0.2, 
    #     num_pelados=10, 
    #     cfc=False,
    #     iteraciones_por_pelado=1, 
    #     iteraciones_difusion=iteraciones_difusion, 
    #     umbral_masa=1.0, 
    #     umbral_nodos_final=max(1, int(0.0001 * num_de_usuarios)), 
    #     masa_total_concentrada=num_de_usuarios,
    #     n_users=num_de_usuarios,
    #     m_neighbors=2,
    #     p_triangle=0.3, 
    #     ratio_mutual=0.5,
    #     generar_visualizaciones=False
    # )