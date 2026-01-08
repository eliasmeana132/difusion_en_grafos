import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go

class MotorDifusion:
    def __init__(self, G, tasa_difusion=0.7):
        self.G = G
        self.tasa_difusion = tasa_difusion

    def ejecutar(self, iteraciones=100):
        es_dirigido = self.G.is_directed()
        for _ in range(iteraciones):
            actualizaciones = {n: 0.0 for n in self.G.nodes()}
            for n in self.G.nodes():
                valor = self.G.nodes[n]['val']
                vecinos = list(self.G.successors(n)) if es_dirigido else list(self.G.neighbors(n))
                if vecinos:
                    mantener = valor * (1 - self.tasa_difusion)
                    actualizaciones[n] += mantener
                    reparto = (valor - mantener) / len(vecinos)
                    for v in vecinos:
                        actualizaciones[v] += reparto
                else:
                    actualizaciones[n] += valor
            for n, v in actualizaciones.items():
                self.G.nodes[n]['val'] = v

class AnalizadorPelado:
    @staticmethod
    def obtener_metricas_cfc(G, version_pelado, total_nodos_original):
        if G.is_directed():
            componentes = list(nx.strongly_connected_components(G))
        else:
            componentes = list(nx.connected_components(G))
        resultados = []
        for i, nodos in enumerate(componentes):
            masa = sum(G.nodes[n]['val'] for n in nodos)
            es_trivial = len(nodos) == 1 and not G.has_edge(list(nodos)[0], list(nodos)[0])
            resultados.append({
                'capa_pelado': version_pelado + 1,
                'id_componente': f"P{version_pelado+1}_C{i}",
                'nodos': sorted(list(nodos)),
                'tamano': len(nodos),
                'es_trivial': es_trivial,
                'masa_total': masa,
                'impacto_global': masa / total_nodos_original if total_nodos_original > 0 else 0
            })
        return sorted(resultados, key=lambda x: x['masa_total'], reverse=True)

class VisualizadorPelado:
    @staticmethod
    def generar_figura_3d(G, titulo):
        if len(G.nodes()) == 0: return None
        pos_3d = nx.spring_layout(G, dim=3, seed=42, k=0.15)
        
        edge_x, edge_y, edge_z = [], [], []
        a_x, a_y, a_z = [], [], [] 
        a_u, a_v, a_w = [], [], [] 

        for edge in G.edges():
            x0, y0, z0 = pos_3d[edge[0]]
            x1, y1, z1 = pos_3d[edge[1]]
            
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_z.extend([z0, z1, None])

            vx, vy, vz = x1 - x0, y1 - y0, z1 - z0
            length = np.sqrt(vx**2 + vy**2 + vz**2)
            
            if length > 0:
                a_x.append(x0 + 0.8 * vx)
                a_y.append(y0 + 0.8 * vy)
                a_z.append(z0 + 0.8 * vz)
                
                a_u.append(vx / length)
                a_v.append(vy / length)
                a_w.append(vz / length)

        trace_edges = go.Scatter3d(
            x=edge_x, y=edge_y, z=edge_z, 
            line=dict(width=1, color='#888'), 
            hoverinfo='none', mode='lines',
            name='Aristas'
        )

        trace_arrows = go.Cone(
            x=a_x, y=a_y, z=a_z,
            u=a_u, v=a_v, w=a_w,
            sizeref=0.05,       
            anchor="tail",
            showscale=False,
            colorscale=[[0, '#666'], [1, '#666']], 
            opacity=0.6,
            name='Dirección'
        )

        masas = [G.nodes[n]['val'] for n in G.nodes()]
        trace_nodes = go.Scatter3d(
            x=[pos_3d[n][0] for n in G.nodes()],
            y=[pos_3d[n][1] for n in G.nodes()],
            z=[pos_3d[n][2] for n in G.nodes()],
            mode='markers',
            marker=dict(
                symbol='circle', 
                size=[2 + (m * 8) for m in masas], 
                color=masas, 
                colorscale='YlOrRd',
                line=dict(color='black', width=0.5),
                colorbar=dict(title='Masa', thickness=15)
            ),
            text=[f"Nodo: {n}<br>Masa: {m:.4f}" for n, m in zip(G.nodes(), masas)],
            hoverinfo='text',
            name='Nodos'
        )

        fig = go.Figure(data=[trace_edges, trace_arrows, trace_nodes])
        fig.update_layout(
            title=titulo,
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                aspectmode='data' 
            ),
            margin=dict(l=0, r=0, b=0, t=40),
            showlegend=False
        )
        return fig

    @staticmethod
    def renderizar_3d(G, titulo, ruta_base):
        fig = VisualizadorPelado.generar_figura_3d(G, titulo)
        if fig:
            ruta_3d = os.path.join(ruta_base, "renders_3d")
            os.makedirs(ruta_3d, exist_ok=True)
            titulo_archivo = titulo.replace(' ', '_')
            fig.write_html(os.path.join(ruta_3d, f"{titulo_archivo}.html"))

    @staticmethod
    def exportar_dashboard_interactivo(figuras_lista, titulos_lista, ruta_base, nombre_archivo="dashboard_interactivo.html"):
        if not figuras_lista: return

        fig_final = go.Figure()
        traces_por_fig = [len(f.data) for f in figuras_lista]
        total_traces = sum(traces_por_fig)
        
        current_trace_idx = 0
        botones = []

        for i, (fig, titulo) in enumerate(zip(figuras_lista, titulos_lista)):
            num_traces = len(fig.data)
            for trace in fig.data:
                trace.visible = (i == 0)
                fig_final.add_trace(trace)

            visibilidad = [False] * total_traces
            for j in range(current_trace_idx, current_trace_idx + num_traces):
                visibilidad[j] = True

            botones.append(dict(
                label=titulo,
                method="update",
                args=[{"visible": visibilidad},
                      {"title": f"Visualización: {titulo}"}]
            ))
            current_trace_idx += num_traces

        fig_final.update_layout(
            updatemenus=[{
                "buttons": botones,
                "direction": "down",
                "showactive": True,
                "x": 0.05, "xanchor": "left",
                "y": 1.1, "yanchor": "top"
            }],
            title=titulos_lista[0],
            scene=dict(xaxis=dict(showbackground=False),
                       yaxis=dict(showbackground=False),
                       zaxis=dict(showbackground=False))
        )

        ruta_final = os.path.join(ruta_base, nombre_archivo)
        fig_final.write_html(ruta_final)

    @staticmethod
    def renderizar(G, titulo, ruta_base, exportar_gephi=True, mostrar_grafico=False, 
                  k_layout=None, alfa_aristas=0.3, tamano_flecha=15):
        if len(G.nodes()) == 0: return
        
        ruta_imagenes = os.path.join(ruta_base, "imagenes_grafos")
        ruta_gephi = os.path.join(ruta_base, "archivos_gephi")
        os.makedirs(ruta_imagenes, exist_ok=True)
        if exportar_gephi: os.makedirs(ruta_gephi, exist_ok=True)

        plt.figure(figsize=(14, 10))
        k_val = k_layout if k_layout else 0.3 
        posicion = nx.spring_layout(G, k=k_val, seed=42)
        
        masas = [G.nodes[n]['val'] for n in G.nodes()]
        tamanos = [100 + (m * 300) for m in masas] 
        
        nodos = nx.draw_networkx_nodes(G, posicion, node_size=tamanos, node_color=masas, 
                                       cmap=plt.cm.YlOrRd, edgecolors='black', linewidths=0.8)
        
        nx.draw_networkx_edges(G, posicion, alpha=alfa_aristas, arrows=True, arrowsize=tamano_flecha,
                               arrowstyle='-|>', edge_color='gray', connectionstyle='arc3,rad=0.1')
        
        nx.draw_networkx_labels(G, posicion, font_size=8, font_family='sans-serif', font_weight='bold')
        plt.colorbar(nodos, label='Masa Acumulada')
        plt.title(titulo, fontsize=15)
        plt.axis('off')
        
        titulo_archivo = titulo.replace(' ', '_')
        plt.savefig(os.path.join(ruta_imagenes, f"{titulo_archivo}.png"), dpi=300, bbox_inches='tight')

        if exportar_gephi:
            G_export = G.copy()
            for n in G_export.nodes():
                G_export.nodes[n]['masa'] = float(G_export.nodes[n]['val'])
            nx.write_gexf(G_export, os.path.join(ruta_gephi, f"{titulo_archivo}.gexf"))

        if mostrar_grafico: plt.show()
        else: plt.close()

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
            
            titulo_p = f"Iteración Pelado {p+1} (Umbral {u_str})"
            fig_p = VisualizadorPelado.generar_figura_3d(self.G, titulo_p)
            if fig_p:
                figuras_interactivas.append(fig_p)
                titulos_interactivos.append(f"Capa {p+1}")

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
            
        return self.registro_maestro

    def exportar_resumen(self, nombre_archivo):
        if not self.ruta_raiz or not self.registro_maestro: return
        df = pd.DataFrame(self.registro_maestro)
        df.to_csv(os.path.join(self.ruta_raiz, nombre_archivo), index=False)
