import time
import math
import statistics
import re
import uuid
import numpy as np
import pandas as pd
import networkx as nx
import os 

from difusion_lib import (
    GeneradorRedes, 
    ControladorPelado, 
    AnalizadorCELF, 
    AnalizadorRIS, 
    VisualizadorPelado, 
    ConvertidorGrafos
)

class ProcesadorSimulacionesWeb:
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
            return f"CELF_{index:02d}"
        elif method == 'ris':
            return f"RIS_{index:02d}"
        elif method == 'pel':
            m = params.get('umbral_masa', 1.0)
            return f"PEL_{index:02d}"
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

    def _ejecutar_difusion_y_metricas(self, label, seeds, G_original, params, titulo_base):
        if not seeds:
            return {}, [], []

        ctrl = ControladorPelado(G_original)
        
        k = len(seeds)
        start_val = params['masa_total'] / k if k > 0 else 0

        _, figs, record_final = ctrl.ejecutar_estudio(
            iteraciones=params['iteraciones'],
            nodos=list(seeds),
            tasa_difusion=params['tasa'],
            valor_inicio=start_val,
            exportar_resultados=False, 
            carpeta_exportacion=None,
            generar_visualizaciones=params['visualizar']
        )

        for i, fig in enumerate(figs):
            state_name = "Initial State" if i == 0 else "Spread Result"
            fig.layout.title.text = f"{titulo_base} | {state_name}"

        n_total = len(G_original)
        n_mojados = self.cantidad_nodos_mojados(record_final)
        
        metricas = {
            f"{label}_Mojados": n_mojados,
            f"{label}_Ratio": n_mojados / n_total if n_total > 0 else 0.0,
            f"{label}_Entropia": self.uniformidad_entropia(record_final),
            f"{label}_Gini": self.gini(record_final),
            f"{label}_Semillas": str(list(seeds)),
            f"{label}_K": k
        }
        
        return metricas, figs, record_final

    def ejecutar_bateria_masiva(
        self,
        execution_plan,
        configuraciones_grafos=[{'tipo': 'malla_netlogo','params': {'dim': 10, 'link_chance': 40}}], 
        graph=nx.DiGraph(),
        n_simulaciones=5, 
        master_folder=None, 
        generar_visualizaciones=False,
        generar_visualizaciones_pelado=False, 
        exportar_resultados=False, 
        tasa_difusion=0.2, 
        iteraciones_difusion=150, 
        masa_total_concentrada=100,
        default_iteraciones_pelado=150,
        default_umbral_masa=1.0,
        default_umbral_nodos=1,
        usar_cfc=False,
        run_baseline=True
    ):
        mapeo_generadores = {
            'malla_netlogo': GeneradorRedes.generar_malla_estocastica_netlogo,
            'cascada': GeneradorRedes.generar_cascada_estricta,
            'flujo_libre': GeneradorRedes.generar_flujo_libre_escala,
            'sbm': GeneradorRedes.generar_sbm_estocastico,
            'gaussiana': GeneradorRedes.generar_red_gaussiana,
            'red_social_realista' : GeneradorRedes.generar_red_social_realista
        }

        resumen_global = []
        mega_recolector_figs = {} 
        
        params_difusion_base = {
            'iteraciones': iteraciones_difusion,
            'tasa': tasa_difusion,
            'masa_total': masa_total_concentrada,
            'exportar': False,
            'visualizar': generar_visualizaciones
        }
        
        isCustomGraph = len(graph.nodes()) != 0
        if isCustomGraph:
            configuraciones_grafos = [configuraciones_grafos[0]] if configuraciones_grafos else [{'tipo': 'custom'}]

        for batch_idx, config in enumerate(configuraciones_grafos):
            if not isCustomGraph:
                tipo = config['tipo']
                params_especificos = config.get('params', {})
            else: 
                tipo = 'Custom'
                params_especificos = 'Custom'
            
            resumen_metricas = []     

            for i in range(n_simulaciones):
                sim_id = f"Sim_{i+1:03d}"
                
                if not isCustomGraph:
                    func_generadora = mapeo_generadores.get(tipo, GeneradorRedes.generar_malla_estocastica_netlogo)
                    resultado_generador = func_generadora(**params_especificos)
                    G_original = resultado_generador[0] if isinstance(resultado_generador, tuple) else resultado_generador
                else: 
                    G_original = graph
                    
                n_total_nodos = len(G_original)
                
                fila_metricas = {
                    "Simulacion_ID": sim_id,
                    "Tipo_Grafo": tipo,
                    "Total_Nodos_Inicial": n_total_nodos,
                }
                
                base_k = 5
                
                if run_baseline:
                    ctrl_peel = ControladorPelado(G_original.copy()) 
                    
                    _, figs_peel, G_survivors, pelados_dict = ctrl_peel.ejecutar_estudio_pelado(
                        generar_visualizaciones=generar_visualizaciones_pelado,
                        num_pelados=10,
                        iteraciones_por_pelado=default_iteraciones_pelado,
                        umbral_masa=default_umbral_masa,
                        umbral_nodos_final=default_umbral_nodos, 
                        tasa_difusion=tasa_difusion,
                        exportar_resultados=False, 
                        usar_cfc=usar_cfc
                    )
                    base_k = len(G_survivors.nodes()) 
                    if base_k == 0: base_k = 1

                    base_pretty_name = self._generate_pretty_name("baseline", {}, 0)

                    if generar_visualizaciones and generar_visualizaciones_pelado:
                        for f_idx, fig in enumerate(figs_peel):
                            fig.layout.title.text = f"Peeling Phase: {base_pretty_name} | Layer {f_idx+1}"
                        mega_recolector_figs[f"{sim_id} - PeelLayers - Baseline"] = figs_peel
                    
                    fila_metricas["Baseline_Survivors_K"] = base_k
                    fila_metricas["Baseline_Layers"] = len(pelados_dict)

                    seeds_baseline = list(G_survivors.nodes())
                    met_baseline, figs_diff_base, _ = self._ejecutar_difusion_y_metricas(
                        "Baseline", seeds_baseline, G_original.copy(), params_difusion_base, f"Diffusion: {base_pretty_name}"
                    )
                    fila_metricas.update(met_baseline)
                    if generar_visualizaciones:
                        mega_recolector_figs[f"{sim_id} - Difusion - Baseline"] = figs_diff_base
                else:
                    fila_metricas["Baseline_Survivors_K"] = 0
                
                method_counters = {'pel': 0, 'celf': 0, 'ris': 0}

                for plan_item in execution_plan:
                    method_name = list(plan_item.keys())[0]
                    method_params = plan_item[method_name]
                    
                    method_counters[method_name] = method_counters.get(method_name, 0) + 1
                    current_idx = method_counters[method_name]
                    
                    run_label = self._generate_run_label(method_name, method_params, current_idx)
                    pretty_name = self._generate_pretty_name(method_name, method_params, current_idx)
                    
                    found_seeds = []
                    start_time_method = time.time()

                    if method_name == 'pel':
                        ctrl_run = ControladorPelado(G_original.copy())
                        
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
                        run_params['exportar_resultados'] = False

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
                    fila_metricas[f"{run_label}_Time"] = time_taken

                    met_results, figs_diff, _ = self._ejecutar_difusion_y_metricas(
                        run_label, found_seeds, G_original.copy(), params_difusion_base, f"Diffusion: {pretty_name}"
                    )
                    
                    fila_metricas.update(met_results)
                    if generar_visualizaciones:
                        mega_recolector_figs[f"{sim_id} - Difusion - {run_label}"] = figs_diff

                resumen_metricas.append(fila_metricas)

            df_tipo = pd.DataFrame(resumen_metricas)
            resumen_global.append(df_tipo)

        if resumen_global:
            df_maestro = pd.concat(resumen_global, ignore_index=True)
            
            base_cols = ["Simulacion_ID", "Tipo_Grafo", "Total_Nodos_Inicial", "Baseline_Survivors_K"]
            metric_cols = [c for c in df_maestro.columns if c not in base_cols]
            metric_cols.sort()
            final_cols = [c for c in base_cols if c in df_maestro.columns] + metric_cols
            
            df_maestro = df_maestro.reindex(columns=final_cols)
            
            return df_maestro, mega_recolector_figs
        
        return pd.DataFrame(), {}