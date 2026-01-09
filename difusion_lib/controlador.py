import os
import networkx as nx
import pandas as pd
from .motor_difusion import MotorDifusion
from .analitica import AnalizadorPelado
from .visualizador import VisualizadorPelado

class ControladorPelado:
    def __init__(self, grafo):
        self.G = grafo.copy()
        self.conteo_nodos_original = len(self.G.nodes())
        self.registro_maestro = [] 
        self.ruta_raiz = None 

    def _preparar_carpetas(self, ruta_destino):
        self.ruta_raiz = ruta_destino
        os.makedirs(ruta_destino, exist_ok=True)
        os.makedirs(os.path.join(ruta_destino, "reportes_datos"), exist_ok=True)
        return ruta_destino

    def ejecutar_estudio_pelado(self, num_pelados=5, iteraciones_por_pelado=150, umbral_masa=1.1,
                                  tasa_difusion=0.7, valor_inicio=1.0, 
                                  mostrar_graficos=False, exportar_resultados=False, 
                                  carpeta_exportacion="simulaciones/ejecucion",
                                  nombre_resumen="reporte_resumen_pelado.csv"):  
        
        if exportar_resultados: self._preparar_carpetas(carpeta_exportacion)
        ruta_datos = os.path.join(self.ruta_raiz, "reportes_datos") if self.ruta_raiz else ""

        figuras_interactivas = []
        titulos_interactivos = []

        masa_total_inicial = sum(valor_inicio.values()) if isinstance(valor_inicio, dict) else float(valor_inicio) * self.conteo_nodos_original
        ratio_umbral = umbral_masa / masa_total_inicial if masa_total_inicial > 0 else 0
        
        print(f"Iniciando Estudio: {self.conteo_nodos_original} nodos.")
        
        for p in range(num_pelados):
            if len(self.G.nodes()) == 0: break
            
            for n in self.G.nodes():
                self.G.nodes[n]['val'] = valor_inicio.get(n, 1.0) if isinstance(valor_inicio, dict) else float(valor_inicio)
            
            masa_total_actual = sum(nx.get_node_attributes(self.G, 'val').values())
            umbral_escalado = ratio_umbral * masa_total_actual
            u_str = f"{umbral_escalado:.4g}"

            motor = MotorDifusion(self.G, tasa_difusion=tasa_difusion)
            motor.ejecutar(iteraciones=iteraciones_por_pelado)
            
            titulo_p = f"Capa {p+1}"
            fig_p = VisualizadorPelado.generar_figura_3d(self.G, titulo_p)
            if fig_p:
                figuras_interactivas.append(fig_p)
                titulos_interactivos.append(titulo_p)

            if exportar_resultados:
                VisualizadorPelado.renderizar(self.G, f"Post-Difusion_P{p+1}", self.ruta_raiz, mostrar_grafico=mostrar_graficos)
                datos_post = [{"nodo": n, "masa": self.G.nodes[n]['val']} for n in self.G.nodes()]
                pd.DataFrame(datos_post).to_csv(os.path.join(ruta_datos, f"masa_P{p+1}.csv"), index=False)
            
            todas_cfcs = AnalizadorPelado.obtener_metricas_cfc(self.G, p, self.conteo_nodos_original)
            a_eliminar = [s for s in todas_cfcs if s['masa_total'] >= umbral_escalado]
            
            if not a_eliminar:
                print(f"Pelado {p+1}: Fin (Umbral no alcanzado).")
                break
                
            print(f"Pelado {p+1}: Eliminando {len(a_eliminar)} componentes.")
            for cfc in a_eliminar:
                cfc['umbral_utilizado'] = umbral_escalado
                self.registro_maestro.append(cfc)
                self.G.remove_nodes_from(cfc['nodos'])
        
        if exportar_resultados and figuras_interactivas:
            VisualizadorPelado.exportar_dashboard_interactivo(
                figuras_interactivas, 
                titulos_interactivos, 
                self.ruta_raiz
            )
            self.exportar_resumen(nombre_resumen)
            
        return self.registro_maestro, figuras_interactivas

    def exportar_resumen(self, nombre_archivo):
        if not self.ruta_raiz or not self.registro_maestro: return
        df = pd.DataFrame(self.registro_maestro)
        df.to_csv(os.path.join(self.ruta_raiz, nombre_archivo), index=False)