import os
import pandas as pd
import networkx as nx
from datetime import datetime
from difusion_lib import *
import time

class ProcesadorSimulaciones:
    def __init__(self):
        pass

    def cantidad_nodos_mojados(self, record):
        return len(set(record))

    def ejecutar_bateria_masiva(
        self,
        metodos=['pel', 'celf', 'ris'],
        configuraciones_grafos=[{'tipo': 'malla_netlogo','params': {'dim': 10, 'link_chance': 40}}], 
        n_simulaciones=5, 
        generar_visualizaciones=False,
        generar_visualizaciones_pelado=False,
        master_folder="simulaciones", 
        usar_cfc=False,
        tasa_difusion=0.2, 
        num_pelados=10, 
        iteraciones_por_pelado=150, 
        iteraciones_difusion=150, 
        umbral_masa=1.0, 
        umbral_nodos_final=1, 
        masa_total_concentrada=100,
        **kwargs_extra
    ):
        params_metodos = kwargs_extra.get('params_metodos', {})

        def obtener_parametro(metodo, nombre, valor_defecto):
            return params_metodos.get(metodo, {}).get(nombre, valor_defecto)
        
        mapeo_generadores = {
            'malla_netlogo': GeneradorRedes.generar_malla_estocastica_netlogo,
            'cascada': GeneradorRedes.generar_cascada_estricta,
            'flujo_libre': GeneradorRedes.generar_flujo_libre_escala,
            'sbm': GeneradorRedes.generar_sbm_estocastico,
            'gaussiana': GeneradorRedes.generar_red_gaussiana,
            'red_social_realista' : GeneradorRedes.generar_red_social_realista
        }

        if not os.path.exists(master_folder):
            os.makedirs(master_folder)

        resumen_global = []

        for config in configuraciones_grafos:
            tipo = config['tipo']
            params_especificos = config.get('params', {})
            
            folder_tipo = os.path.join(master_folder, f"Estudio_{tipo}")
            if not os.path.exists(folder_tipo): os.makedirs(folder_tipo)

            resumen_metricas = []     

            print(f"\n" + "="*50)
            print(f"INICIANDO BATERÍA: {tipo.upper()} ({n_simulaciones} sims)")
            print(f"Parámetros: {params_especificos}")
            print("="*50)
            mega_recolector_figs = {} 
            
            for i in range(n_simulaciones):
                sim_id = f"Simulacion_{i+1:03d}" 
                print(f">>> {tipo} - {sim_id}")

                func_generadora = mapeo_generadores[tipo]
                resultado_generador = func_generadora(**params_especificos)
                G_original = resultado_generador[0] if isinstance(resultado_generador, tuple) else resultado_generador
                n_total_nodos = len(G_original)
                
                figs_peel = []
                figs_PEL = []
                figs_CELF = []
                figs_RIS = []
                
                n_mojados_PEL = 0
                ratio_val_PEL = 0.0
                tiempo_eje_PEL = 0.0
                
                n_mojados_CELF = 0
                ratio_val_CELF = 0.0
                tiempo_eje_CELF = 0.0
                seeds_celf = []

                n_mojados_RIS = 0
                ratio_val_RIS = 0.0
                tiempo_eje_RIS = 0.0
                seeds_ris = []
                
                ############################################
                # ESTUDIO PELADO
                ############################################
                ctrl_peel = ControladorPelado(G_original)
                folder_sim = os.path.join(folder_tipo, sim_id)
                
                start_time = time.time()
                _, figs_peel, G_survivors, pelados_dict = ctrl_peel.ejecutar_estudio_pelado(
                    generar_visualizaciones=generar_visualizaciones_pelado,
                    num_pelados=num_pelados,
                    iteraciones_por_pelado=iteraciones_por_pelado,
                    umbral_masa=umbral_masa,
                    umbral_nodos_final=umbral_nodos_final, 
                    tasa_difusion=tasa_difusion,
                    exportar_resultados=True,
                    carpeta_exportacion=folder_sim,
                    usar_cfc=usar_cfc
                )
                tiempo_eje_PEL = time.time() - start_time
                
                for idx, fig in enumerate(figs_peel):
                    fig.layout.title.text = f"Peel Step {idx+1}"
                
                if 'pel' in metodos:
                    ctrl_PEL = ControladorPelado(G_original)
                    folder_PEL = os.path.join(folder_sim, "Difusion_PEL")
                    
                    _, figs_PEL, record_final_PEL = ctrl_PEL.ejecutar_estudio(
                        iteraciones=iteraciones_difusion,
                        nodos=list(G_survivors.nodes()), 
                        tasa_difusion=tasa_difusion,
                        valor_inicio=masa_total_concentrada/len(G_survivors) if len(G_survivors)>0 else 0,             
                        exportar_resultados=True,
                        carpeta_exportacion=folder_PEL,
                        generar_visualizaciones=generar_visualizaciones
                    )
                    
                    for fig in figs_PEL:
                        fig.layout.title.text = "Difusión: Método PEL (Peel)"
                    
                    n_mojados_PEL = self.cantidad_nodos_mojados(record_final_PEL)
                    ratio_val_PEL = n_mojados_PEL / n_total_nodos if n_total_nodos > 0 else 0.0
                ############################################
                # FIN ESTUDIO PEL
                ############################################
                
                ############################################
                # ESTUDIO CELF
                ############################################
                if 'celf' in metodos and len(G_survivors) > 0:
                    G_ig = ConvertidorGrafos.a_igraph(G_original)
                    k=len(G_survivors)
                    p = obtener_parametro('celf', 'p', 0.1)
                    mc = obtener_parametro('celf', 'mc', 100)

                    print(f"Iniciando CELF...")
                    start_celf=time.time()
                    seeds_celf, spreads, times, lookups = AnalizadorCELF.ejecutar_celf(g=G_ig, k=k, p=p, mc=mc)
                    tiempo_eje_CELF=time.time()-start_celf

                    ctrl_CELF = ControladorPelado(G_original)
                    folder_CELF = os.path.join(folder_sim, "Difusion_CELF")
                    
                    _, figs_CELF, record_final_CELF = ctrl_CELF.ejecutar_estudio(
                        iteraciones=iteraciones_difusion,
                        nodos=list(seeds_celf),
                        tasa_difusion=tasa_difusion,
                        valor_inicio=masa_total_concentrada/len(G_survivors) if len(G_survivors)>0 else 0,
                        exportar_resultados=True,
                        carpeta_exportacion=folder_CELF,
                        generar_visualizaciones=generar_visualizaciones
                    )
                    
                    for fig in figs_CELF:
                        fig.layout.title.text = "Difusión: Método CELF"
                    
                    n_mojados_CELF = self.cantidad_nodos_mojados(record_final_CELF)
                    ratio_val_CELF = n_mojados_CELF / n_total_nodos if n_total_nodos > 0 else 0.0
                    
                ############################################
                # FIN ESTUDIO CELF
                ############################################
                
                ############################################
                # ESTUDIO RIS
                ############################################
                if 'ris' in metodos and len(G_survivors) > 0:
                    G_df_edges = nx.to_pandas_edgelist(G_original)
                    k_ris = len(G_survivors)
                    p_ris = obtener_parametro('ris', 'p', 0.01)
                    mc_ris = obtener_parametro('ris', 'mc', 5000)           
                    
                    print(f"Iniciando RIS...")
                    start_ris = time.time()
                    seeds_ris, times_ris = AnalizadorRIS.ris(G=G_df_edges, k=k_ris, p=p_ris, mc=mc_ris)
                    tiempo_eje_RIS = time.time() - start_ris

                    ctrl_RIS = ControladorPelado(G_original)
                    folder_RIS = os.path.join(folder_sim, "Difusion_RIS")
                    
                    _, figs_RIS, record_final_RIS = ctrl_RIS.ejecutar_estudio(
                        iteraciones=iteraciones_difusion,
                        nodos=list(seeds_ris), 
                        tasa_difusion=tasa_difusion,
                        valor_inicio=masa_total_concentrada/len(G_survivors) if len(G_survivors)>0 else 0,             
                        exportar_resultados=True,
                        carpeta_exportacion=folder_RIS,
                        generar_visualizaciones=generar_visualizaciones
                    )
                    
                    for fig in figs_RIS:
                        fig.layout.title.text = "Difusión: Método RIS"
                    
                    n_mojados_RIS = self.cantidad_nodos_mojados(record_final_RIS)
                    ratio_val_RIS = n_mojados_RIS / n_total_nodos if n_total_nodos > 0 else 0.0
                
                ############################################
                # FIN ESTUDIO RIS
                ############################################
                
                ############################################
                # MEGA DASHBOARD 
                ############################################
                if generar_visualizaciones:
                    mega_recolector_figs[f"{sim_id} - Estudio Pelado"] = figs_peel
                    
                    if 'pel' in metodos:
                        mega_recolector_figs[f"{sim_id} - Difusion - PEL"] = figs_PEL
                    
                    if 'celf' in metodos:
                        mega_recolector_figs[f"{sim_id} - Difusion - CELF"] = figs_CELF
                    
                    if 'ris' in metodos:
                        mega_recolector_figs[f"{sim_id} - Difusion - RIS"] = figs_RIS

                resumen_metricas.append({
                    "Simulacion_ID": sim_id,
                    "Tipo_Grafo": tipo, 
                    "Total_Nodos_Inicial": n_total_nodos,
                    "Total_Capas_Peladas": len(pelados_dict),
                    "Cantidad_Semillas_PEL": len(G_survivors.nodes),
                    "Semillas_PEL": str(list(G_survivors.nodes())),
                    "Nodos_Mojados_PEL": n_mojados_PEL,
                    "Ratio_Mojados_PEL": ratio_val_PEL,
                    "Tiempo_Eje_PEL": tiempo_eje_PEL,
                    "Semillas_CELF": str(seeds_celf),
                    "Nodos_Mojados_CELF": n_mojados_CELF,
                    "Ratio_Mojados_CELF": ratio_val_CELF,
                    "tiempo_eje_CELF": tiempo_eje_CELF,
                    "Semillas_RIS": str(seeds_ris),
                    "Nodos_Mojados_RIS": n_mojados_RIS,
                    "Ratio_Mojados_RIS": ratio_val_RIS,
                    "Tiempo_Eje_RIS": tiempo_eje_RIS,
                })

            if generar_visualizaciones:
                VisualizadorPelado.exportar_mega_dashboard(
                    mega_recolector_figs,
                    folder_tipo,
                    f"Dashboard_Global_{tipo}.html"
                )

            df_tipo = pd.DataFrame(resumen_metricas)
            df_tipo.to_csv(os.path.join(folder_tipo, f"Metricas_{tipo}_{time.time()}.csv"), index=False)
            resumen_global.append(df_tipo)

        print("\nGenerando reportes consolidados...")
        df_maestro = pd.concat(resumen_global, ignore_index=True)
        df_maestro.to_csv(os.path.join(master_folder, f"Metricas_Globales_Detalladas_{time.time()}.csv"), index=False)
        
        columnas_interes = [
            "Tipo_Grafo", "Total_Nodos_Inicial", "Total_Capas_Peladas", 
            "Cantidad_Semillas_PEL", "Nodos_Mojados_PEL", "Ratio_Mojados_PEL", "Tiempo_Eje_PEL",
            "Nodos_Mojados_CELF", "Ratio_Mojados_CELF", "tiempo_eje_CELF",
            "Nodos_Mojados_RIS", "Ratio_Mojados_RIS", "Tiempo_Eje_RIS"
        ]
        df_promedios = df_maestro[columnas_interes].groupby("Tipo_Grafo").mean().reset_index()
        df_promedios.to_csv(os.path.join(master_folder, f"Promedios_Globales_Bateria_{time.time()}.csv"), index=False)
        
        print("=== TODAS LAS BATERÍAS COMPLETADAS ===")
