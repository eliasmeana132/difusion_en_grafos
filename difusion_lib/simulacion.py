import os
import time
import math
import statistics
import re
import uuid
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from difusion_lib import (
    GeneradorRedes, 
    ControladorPelado, 
    AnalizadorCELF, 
    AnalizadorRIS, 
    VisualizadorPelado, 
    ConvertidorGrafos
)

class ProcesadorSimulaciones:
    def __init__(self):
        pass

    @staticmethod
    def cantidad_nodos_mojados(record):
        return np.count_nonzero(record)
    
    @staticmethod
    def coeficiente_variacion(record):
        arr = np.array(record)
        arr = arr[arr > 0]
        if len(arr) == 0:
            return 0.0
        mean = np.mean(arr)
        return np.std(arr) / mean if mean != 0 else 0.0

    @staticmethod
    def uniformidad_entropia(record):
        arr = np.array(record)
        arr = arr[arr > 0]
        total = np.sum(arr)
        if total == 0:
            return 0.0
        probs = arr / total
        return -np.sum(probs * np.log(probs))

    @staticmethod
    def gini(record):
        arr = np.array(record)
        arr = arr[arr > 0]
        arr = np.sort(arr)
        n = len(arr)
        if n == 0:
            return 0.0
        index = np.arange(1, n + 1)
        return (2 * np.sum(index * arr)) / (n * np.sum(arr)) - (n + 1) / n

    def _generate_run_label(self, method, params, index):
        if method == 'celf':
            return f"CELF_{index:02d}_p{params.get('p', 0.1)}_k{params.get('k', 'Auto')}"
        elif method == 'ris':
            return f"RIS_{index:02d}_p{params.get('p', 0.01)}_k{params.get('k', 'Auto')}"
        elif method == 'pel':
            m = params.get('umbral_masa', 1.0)
            i = params.get('iteraciones_por_pelado', 150)
            return f"PEL_{index:02d}_M{m}_I{i}"
        return f"{method.upper()}_{index:02d}"

    def _generate_pretty_name(self, method, params, index):
        if method == 'baseline':
            return "Baseline (Calibration)"
        elif method == 'celf':
            return f"CELF #{index}"
        elif method == 'ris':
            return f"RIS #{index}"
        elif method == 'pel':
            m = params.get('umbral_masa', 1.0)
            return f"Peeling #{index} (Mass>{m})"
        return f"{method.upper()} #{index}"

    def _ejecutar_difusion_y_metricas(self, label, seeds, G_original, params, folder_base, titulo_base):
        if not seeds:
            return {}, [], []

        ctrl = ControladorPelado(G_original)
        folder_export = os.path.join(folder_base, f"Difusion_{label}")
        
        k = len(seeds)
        start_val = params['masa_total'] / k if k > 0 else 0

        _, figs, record_final = ctrl.ejecutar_estudio(
            iteraciones=params['iteraciones'],
            nodos=list(seeds),
            tasa_difusion=params['tasa'],
            valor_inicio=start_val,
            exportar_resultados=params['exportar'],
            carpeta_exportacion=folder_export,
            generar_visualizaciones=params['visualizar']
        )

        for i, fig in enumerate(figs):
            state_name = "Initial State" if i == 0 else "Spread Result"
            fig.layout.title.text = f"{titulo_base} | {state_name}"

        n_total = len(G_original)
        n_mojados = self.cantidad_nodos_mojados(record_final)
        
        metricas = {
            f"Nodos_Mojados_{label}": n_mojados,
            f"Ratio_Mojados_{label}": n_mojados / n_total if n_total > 0 else 0.0,
            f"Entropia_{label}": self.uniformidad_entropia(record_final),
            f"Gini_{label}": self.gini(record_final),
            f"cv_{label}": self.coeficiente_variacion(record_final),
            f"Semillas_{label}": str(list(seeds)),
            f"K_{label}": k
        }
        
        return metricas, figs, record_final

    def ejecutar_bateria_masiva(
        self,
        execution_plan,
        configuraciones_grafos=[{'tipo': 'malla_netlogo','params': {'dim': 10, 'link_chance': 40}}], 
        graph=nx.DiGraph(),
        n_simulaciones=5, 
        master_folder="simulaciones", 
        generar_visualizaciones=False,
        generar_visualizaciones_pelado=False, 
        exportar_resultados=True,
        tasa_difusion=0.2, 
        iteraciones_difusion=150, 
        masa_total_concentrada=100,
        default_iteraciones_pelado=150,
        default_umbral_masa=1.0,
        default_umbral_nodos=1,
        usar_cfc=False
    ):
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
        
        params_difusion_base = {
            'iteraciones': iteraciones_difusion,
            'tasa': tasa_difusion,
            'masa_total': masa_total_concentrada,
            'exportar': exportar_resultados,
            'visualizar': generar_visualizaciones
        }
        
        isCustomGraph = len(graph.nodes()) != 0
        if isCustomGraph:
            configuraciones_grafos = [1]

        for batch_idx, config in enumerate(configuraciones_grafos):
            if not isCustomGraph:
                tipo = config['tipo']
                params_especificos = config.get('params', {})
                params_raw_str = str(params_especificos)
            else: 
                tipo = 'Custom'
                params_especificos = 'Custom'
                params_raw_str = "Custom"
            
            safe_params_str = re.sub(r'[<>:"/\\|?*{}\',; \[\]]+', '_', params_raw_str)
            safe_params_str = re.sub(r'_+', '_', safe_params_str).strip('_')

            if exportar_resultados:
                folder_tipo = os.path.join(master_folder, f"Estudio_{tipo}_{safe_params_str}")
                if not os.path.exists(folder_tipo): 
                    os.makedirs(folder_tipo)
            else:
                folder_tipo = ""

            resumen_metricas = []     
            mega_recolector_figs = {} 

            print(f"\n" + "="*50)
            print(f"INICIANDO BATERÍA {batch_idx+1}: {tipo.upper()} ({n_simulaciones} sims)")
            print(f"Parámetros: {params_especificos}")
            print("="*50)
            
            for i in range(n_simulaciones):
                sim_id = f"Simulacion_{i+1:03d}" 
                print(f">>> {tipo} - {sim_id}")
                
                if not isCustomGraph:
                    func_generadora = mapeo_generadores[tipo]
                    resultado_generador = func_generadora(**params_especificos)
                    G_original = resultado_generador[0] if isinstance(resultado_generador, tuple) else resultado_generador
                else: 
                    G_original = graph
                    
                n_total_nodos = len(G_original)
                
                folder_sim = os.path.join(folder_tipo, sim_id) if exportar_resultados else ""

                ctrl_peel = ControladorPelado(G_original.copy()) 
                start_peel_base = time.time()
                _, figs_peel, G_survivors, pelados_dict = ctrl_peel.ejecutar_estudio_pelado(
                    generar_visualizaciones=generar_visualizaciones_pelado,
                    num_pelados=10,
                    iteraciones_por_pelado=default_iteraciones_pelado,
                    umbral_masa=default_umbral_masa,
                    umbral_nodos_final=default_umbral_nodos, 
                    tasa_difusion=tasa_difusion,
                    exportar_resultados=exportar_resultados,
                    carpeta_exportacion=os.path.join(folder_sim, "Baseline_Peel"),
                    usar_cfc=usar_cfc
                )
                base_k = len(G_survivors.nodes()) 

                base_pretty_name = self._generate_pretty_name("baseline", {}, 0)

                if generar_visualizaciones and generar_visualizaciones_pelado:
                    for f_idx, fig in enumerate(figs_peel):
                        fig.layout.title.text = f"Peeling Phase: {base_pretty_name} | Layer {f_idx+1}"
                    mega_recolector_figs[f"{sim_id} - PeelLayers - Baseline"] = figs_peel

                fila_metricas = {
                    "Simulacion_ID": sim_id,
                    "Tipo_Grafo": tipo + str(params_raw_str), 
                    "Batch_ID": batch_idx,
                    "Total_Nodos_Inicial": n_total_nodos,
                    "Baseline_Survivors_K": base_k,
                    "Baseline_Layers": len(pelados_dict)
                }

                seeds_baseline = list(G_survivors.nodes())
                met_baseline, figs_diff_base, _ = self._ejecutar_difusion_y_metricas(
                    "Baseline", seeds_baseline, G_original.copy(), params_difusion_base, folder_sim, f"Diffusion Simulation: {base_pretty_name}"
                )
                fila_metricas.update(met_baseline)
                if generar_visualizaciones:
                    mega_recolector_figs[f"{sim_id} - Difusion - Baseline"] = figs_diff_base

                method_counters = {'pel': 0, 'celf': 0, 'ris': 0}

                for plan_item in execution_plan:
                    method_name = list(plan_item.keys())[0]
                    method_params = plan_item[method_name]
                    
                    method_counters[method_name] = method_counters.get(method_name, 0) + 1
                    current_idx = method_counters[method_name]
                    
                    run_label = self._generate_run_label(method_name, method_params, current_idx)
                    pretty_name = self._generate_pretty_name(method_name, method_params, current_idx)
                    
                    print(f"   Running {pretty_name}...")

                    found_seeds = []
                    start_time_method = time.time()

                    if method_name == 'pel':
                        ctrl_run = ControladorPelado(G_original.copy())
                        
                        user_path = method_params.get('carpeta_exportacion', folder_sim)
                        user_filename = method_params.get('nombre_resumen', f"resumen_pelado.csv")
                        
                        unique_id = str(uuid.uuid4())[:8]
                        unique_export_path = os.path.join(user_path, f"Sim_{i+1:03d}_{run_label}_{unique_id}")
                        if not os.path.exists(unique_export_path):
                            os.makedirs(unique_export_path)

                        if user_filename.endswith('.csv'):
                            unique_filename = user_filename.replace('.csv', f"_{run_label}_{unique_id}.csv")
                        else:
                            unique_filename = f"{user_filename}_{run_label}_{unique_id}.csv"

                        run_params = {
                            'num_pelados': 10,
                            'iteraciones_por_pelado': default_iteraciones_pelado,
                            'umbral_masa': default_umbral_masa,
                            'umbral_nodos_final': default_umbral_nodos,
                            'tasa_difusion': tasa_difusion,
                            'valor_inicio': masa_total_concentrada / n_total_nodos if n_total_nodos > 0 else 0,
                            'mostrar_graficos': False,
                            'exportar_resultados': False,
                            'generar_visualizaciones': generar_visualizaciones, 
                            'usar_cfc': usar_cfc
                        }
                        
                        run_params.update(method_params)
                        run_params['carpeta_exportacion'] = unique_export_path
                        run_params['nombre_resumen'] = unique_filename

                        _, figs_run, G_surv_run, _ = ctrl_run.ejecutar_estudio_pelado(**run_params)
                        found_seeds = list(G_surv_run.nodes())

                        if generar_visualizaciones:
                            for f_idx, fig in enumerate(figs_run):
                                fig.layout.title.text = f"Peeling Phase: {pretty_name} | Layer {f_idx+1}"
                            mega_recolector_figs[f"{sim_id} - PeelLayers - {run_label}"] = figs_run

                    elif method_name == 'celf':
                        target_k = method_params.get('k', base_k)
                        if target_k == 0: target_k = 1

                        G_ig = ConvertidorGrafos.a_igraph(G_original)
                        p_celf = method_params.get('p', 0.1)
                        mc_celf = method_params.get('mc', 100)
                        
                        found_seeds, _, _, _ = AnalizadorCELF.ejecutar_celf(g=G_ig, k=target_k, p=p_celf, mc=mc_celf)

                    elif method_name == 'ris':
                        target_k = method_params.get('k', base_k)
                        if target_k == 0: target_k = 1

                        G_df_edges = nx.to_pandas_edgelist(G_original)
                        p_ris = method_params.get('p', 0.01)
                        mc_ris = method_params.get('mc', 1000)

                        found_seeds, _ = AnalizadorRIS.ris(G=G_df_edges, k=target_k, p=p_ris, mc=mc_ris)

                    time_taken = time.time() - start_time_method
                    fila_metricas[f"Time_Exec_{run_label}"] = time_taken

                    met_results, figs_diff, _ = self._ejecutar_difusion_y_metricas(
                        run_label, found_seeds, G_original.copy(), params_difusion_base, folder_sim, f"Diffusion Simulation: {pretty_name}"
                    )
                    
                    fila_metricas.update(met_results)
                    if generar_visualizaciones:
                        mega_recolector_figs[f"{sim_id} - Difusion - {run_label}"] = figs_diff

                resumen_metricas.append(fila_metricas)

            if generar_visualizaciones:
                VisualizadorPelado.exportar_mega_dashboard(
                    mega_recolector_figs,
                    folder_tipo,
                    f"Dashboard_Global_{tipo}.html"
                )
            
            if exportar_resultados:
                df_tipo = pd.DataFrame(resumen_metricas)
                base_cols = ["Simulacion_ID", "Tipo_Grafo", "Batch_ID", "Total_Nodos_Inicial", "Baseline_Survivors_K"]
                metric_cols = [c for c in df_tipo.columns if c not in base_cols]
                metric_cols.sort()
                final_cols = base_cols + metric_cols
                
                df_tipo = df_tipo.reindex(columns=final_cols)
                
                csv_unique_suffix = f"{int(time.time())}_{batch_idx}"
                df_tipo.to_csv(os.path.join(folder_tipo, f"Metricas_{tipo}_{csv_unique_suffix}.csv"), index=False)
                resumen_global.append(df_tipo)

        if exportar_resultados and resumen_global:
            print("\nGenerando reportes consolidados...")
            df_maestro = pd.concat(resumen_global, ignore_index=True)
            df_maestro.to_csv(os.path.join(master_folder, f"Metricas_Globales_Master_{int(time.time())}.csv"), index=False)
            
            numeric_cols = df_maestro.select_dtypes(include=[np.number]).columns.tolist()
            cols_to_group = ["Tipo_Grafo"]
            if "Batch_ID" in df_maestro.columns:
                 pass
            
            if cols_to_group:
                existing_groups = [c for c in cols_to_group if c in df_maestro.columns]
                df_promedios = df_maestro.groupby(existing_groups)[numeric_cols].mean().reset_index()
                df_promedios.to_csv(os.path.join(master_folder, f"Promedios_Globales_{int(time.time())}.csv"), index=False)