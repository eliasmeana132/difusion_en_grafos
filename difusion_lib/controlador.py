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

    def ejecutar_estudio_pelado(self, num_pelados=5, iteraciones_por_pelado=150, umbral_masa=1.1,umbral_nodos_final=1,
                                  tasa_difusion=0.7, valor_inicio=1.0, 
                                  mostrar_graficos=False, exportar_resultados=False, 
                                  carpeta_exportacion="simulaciones/ejecucion",
                                  nombre_resumen="reporte_resumen_pelado.csv"):  
        
        if exportar_resultados: self._preparar_carpetas(carpeta_exportacion)
        ruta_datos = os.path.join(self.ruta_raiz, "reportes_datos") if self.ruta_raiz else ""

        figuras_interactivas = []
        titulos_interactivos = []
        
        print(f"Iniciando Estudio: {self.conteo_nodos_original} nodos.")
        pelados={}
        for p in range(num_pelados):
            if len(self.G.nodes()) == 0: break
            
            for n in self.G.nodes():
                self.G.nodes[n]['val'] = valor_inicio.get(n, 1.0) if isinstance(valor_inicio, dict) else float(valor_inicio)
            
            umbral_escalado = umbral_masa

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
            
            # todas_cfcs = AnalizadorPelado.obtener_metricas_cfc(self.G, p, self.conteo_nodos_original)
            todas_cfcs = AnalizadorPelado.nodos_para_quitar(self.G,p,self.conteo_nodos_original,umbral_masa=1.0)
            a_eliminar = [s for s in todas_cfcs if s['masa_total'] >= umbral_escalado]
            
            if not a_eliminar:
                print(f"Pelado {p+1}: Fin (Umbral no alcanzado).")
                break
                
            print(f"Pelado {p+1}: Eliminando {len(a_eliminar)} componentes.")
            if len(self.G.nodes)-len(a_eliminar)<umbral_nodos_final:
                    break
            for cfc in a_eliminar:
                cfc['umbral_utilizado'] = umbral_escalado
                self.registro_maestro.append(cfc)
                self.G.remove_nodes_from(cfc['nodos'])
            pelados.update({p+1: a_eliminar[0]['nodos']})
        
        if exportar_resultados and figuras_interactivas:
            VisualizadorPelado.exportar_dashboard_interactivo(
                figuras_interactivas, 
                titulos_interactivos, 
                self.ruta_raiz
            )
            self.exportar_resumen(nombre_resumen)
            
        return self.registro_maestro, figuras_interactivas,self.G,pelados
    
    def ejecutar_estudio(self, iteraciones=150, nodos=[], tasa_difusion=0.7, valor_inicio=1.0, 
                                  mostrar_graficos=False, exportar_resultados=False, 
                                  carpeta_exportacion="simulaciones/ejecucion",
                                  nombre_resumen="reporte_resumen_pelado.csv"):  
        
        if exportar_resultados: self._preparar_carpetas(carpeta_exportacion)
        ruta_datos = os.path.join(self.ruta_raiz, "reportes_datos") if self.ruta_raiz else ""

        figuras_interactivas = []
        titulos_interactivos = []
        
        print(f"Iniciando Difusión: {self.conteo_nodos_original} nodos.")
        
        if len(self.G.nodes()) == 0: 
            return 'Por favor espicifica los nodos iniciales.'
            
        for n in self.G.nodes:
            if n in nodos:
                self.G.nodes[n]['val'] = valor_inicio.get(n, 1.0) if isinstance(valor_inicio, dict) else float(valor_inicio)
            else: 
                self.G.nodes[n]['val'] = 0
        motor = MotorDifusion(self.G, tasa_difusion=tasa_difusion)
        record = [0]*len(self.G.nodes)
        for i in range(iteraciones):
            motor.ejecutar(iteraciones=1)
            for n in self.G.nodes:
                if self.G.nodes[n]['val']>record[n]:
                    record[n]=self.G.nodes[n]['val']
                    
        titulo_p = f"Difusion Final"
        fig_p = VisualizadorPelado.generar_figura_3d(self.G, titulo_p)
        if fig_p:
            figuras_interactivas.append(fig_p)
            titulos_interactivos.append(titulo_p)

        if exportar_resultados:
            VisualizadorPelado.renderizar(self.G, f"Post-Difusion_Final", self.ruta_raiz, mostrar_grafico=mostrar_graficos)
            datos_post = [{"nodo": n, "masa": record[n]} for n in self.G.nodes()]
            pd.DataFrame(datos_post).to_csv(os.path.join(ruta_datos, f"Masa_Final.csv"), index=False)       
        if exportar_resultados:
            VisualizadorPelado.exportar_dashboard_interactivo(
                figuras_interactivas, 
                titulos_interactivos, 
                self.ruta_raiz
            )
            self.exportar_resumen(nombre_resumen)
            
        return self.registro_maestro, figuras_interactivas,record

    def exportar_resumen(self, nombre_archivo):
        if not self.ruta_raiz or not self.registro_maestro: return
        df = pd.DataFrame(self.registro_maestro)
        df.to_csv(os.path.join(self.ruta_raiz, nombre_archivo), index=False)