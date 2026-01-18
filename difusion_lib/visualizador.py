import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import os
import plotly.graph_objects as go
import pickle


class _Geometry3D:
    @staticmethod
    def calculate_layout(G, seed=42, k=0.15):
        return nx.spring_layout(G, dim=3, seed=seed, k=k)

    @staticmethod
    def get_edge_coordinates(G, pos_3d):
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
                a_x.append(x0 + 0.9 * vx)
                a_y.append(y0 + 0.9 * vy)
                a_z.append(z0 + 0.9 * vz)
                a_u.append(vx / length)
                a_v.append(vy / length)
                a_w.append(vz / length)
                
        return (edge_x, edge_y, edge_z), (a_x, a_y, a_z, a_u, a_v, a_w)

class _TraceBuilder:
    @staticmethod
    def create_edge_trace(coords):
        x, y, z = coords
        return go.Scatter3d(
            x=x, y=y, z=z, 
            line=dict(width=1, color='#dbdbdb'), 
            hoverinfo='none', mode='lines', name='Aristas'
        )

    @staticmethod
    def create_arrow_trace(vectors):
        x, y, z, u, v, w = vectors
        return go.Cone(
            x=x, y=y, z=z, u=u, v=v, w=w, 
            sizeref=0.5, anchor="tail", showscale=False, 
            colorscale=[[0, '#dbdbdb'], [1, '#dbdbdb']], opacity=0.6, name='Dirección'
        )

    @staticmethod
    def create_node_trace(G, pos_3d, min_size=2, scalar=8):
        masas = [G.nodes[n].get('val', 1.0) for n in G.nodes()]
        x = [pos_3d[n][0] for n in G.nodes()]
        y = [pos_3d[n][1] for n in G.nodes()]
        z = [pos_3d[n][2] for n in G.nodes()]
        
        return go.Scatter3d(
            x=x, y=y, z=z,
            mode='markers',
            marker=dict(
                symbol='circle', 
                size=[min_size + (m * scalar) for m in masas], 
                color=masas, 
                colorscale='YlOrRd', 
                line=dict(color='black', width=0.5), 
                showscale=True, 
                colorbar=dict(title='Masa', thickness=15)
            ),
            text=[f"Nodo: {n}<br>Masa: {m:.4f}" for n, m in zip(G.nodes(), masas)], 
            hoverinfo='text', name='Nodos'
        )

class _DashboardManager:
    @staticmethod
    def get_global_mass_range(diccionario_simulaciones):
        all_masses = []
        for list_figs in diccionario_simulaciones.values():
            for f in list_figs:
                if len(f.data) > 2:
                    all_masses.extend(f.data[2].marker.color)
        return (min(all_masses), max(all_masses)) if all_masses else (0, 1)

    @staticmethod
    def create_dummy_colorbar(min_m, max_m):
        return go.Scatter3d(
            x=[None], y=[None], z=[None], mode='markers',
            marker=dict(
                colorscale='YlOrRd', cmin=min_m, cmax=max_m, showscale=True,
                colorbar=dict(title='Masa', thickness=20, x=1.0, len=0.7, y=0.5)
            ), showlegend=False
        )

    @staticmethod
    def add_traces_to_master(fig_final, diccionario_simulaciones, start_idx=1):
        mapeo = []
        counter = start_idx
        
        for sim_nombre, lista_figs in diccionario_simulaciones.items():
            for i, fig in enumerate(lista_figs):
                num_trazas = len(fig.data)
                indices = list(range(counter, counter + num_trazas))
                
                for trace in fig.data:
                    trace.visible = False
                    trace.showlegend = False
                    if hasattr(trace, 'marker') and trace.marker and hasattr(trace.marker, 'showscale'):
                        trace.marker.showscale = False
                    fig_final.add_trace(trace)
                
                mapeo.append({"sim": sim_nombre, "capa": i, "indices": indices})
                counter += num_trazas
        return mapeo

    @staticmethod
    def generate_buttons(diccionario_simulaciones, mapeo_trazas, total_traces):
        botones = []
        for sim_nombre in diccionario_simulaciones.keys():
            max_capas = len(diccionario_simulaciones[sim_nombre])
            for c in range(max_capas):
                visibilidad = [False] * total_traces
                visibilidad[0] = True 
                
                for m in mapeo_trazas:
                    if m["sim"] == sim_nombre and m["capa"] == c:
                        for idx in m["indices"]: visibilidad[idx] = True
                
                botones.append(dict(
                    label=f"{sim_nombre} - Capa {c+1}", 
                    method="update", 
                    args=[{"visible": visibilidad}, {"title": f"Red: {sim_nombre} | Capa {c+1}"}]
                ))
        return botones

class VisualizadorPelado:
    
    @staticmethod
    def generar_figura_3d(G, titulo, node_min=5, node_scale=3):

        if len(G.nodes()) == 0: return None
        
        pos_3d = _Geometry3D.calculate_layout(G)
        coords_edges, coords_arrows = _Geometry3D.get_edge_coordinates(G, pos_3d)
        
        trace_edges = _TraceBuilder.create_edge_trace(coords_edges)
        trace_arrows = _TraceBuilder.create_arrow_trace(coords_arrows)
        
        trace_nodes = _TraceBuilder.create_node_trace(G, pos_3d, min_size=node_min, scalar=node_scale)
        
        fig = go.Figure(data=[trace_edges, trace_arrows, trace_nodes])
        fig.update_layout(
            title=titulo, 
            scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), aspectmode='data'), 
            margin=dict(l=0, r=0, b=0, t=40), 
            showlegend=False
        )
        return fig

    @staticmethod
    def renderizar_3d(G, titulo, ruta_base, node_min=2, node_scale=8):
        fig = VisualizadorPelado.generar_figura_3d(G, titulo, node_min, node_scale)
        if fig:
            ruta_3d = os.path.join(ruta_base, "renders_3d")
            os.makedirs(ruta_3d, exist_ok=True)
            fig.write_html(os.path.join(ruta_3d, f"{titulo.replace(' ', '_')}.html"))

    @staticmethod
    def exportar_dashboard_interactivo(figuras_lista, titulos_lista, ruta_base, nombre_archivo="dashboard_interactivo.html"):
        VisualizadorPelado.exportar_mega_dashboard({"Resultados": figuras_lista}, ruta_base, nombre_archivo)

    @staticmethod
    def renderizar(G, titulo, ruta_base, exportar_gephi=True, mostrar_grafico=False, k_layout=None, alfa_aristas=0.3, tamano_flecha=15, node_base=100, node_scale=300, formatos=["svg"]):
        if len(G.nodes()) == 0: return
        
        ruta_imagenes = os.path.join(ruta_base, "imagenes_grafos")
        os.makedirs(ruta_imagenes, exist_ok=True)
        
        fig = plt.figure(figsize=(14, 10))
        
        posicion = nx.spring_layout(G, k=k_layout if k_layout else 0.3, seed=42)
        masas = [G.nodes[n].get('val', 1.0) for n in G.nodes()]
        
        nx.draw_networkx_nodes(G, posicion, 
            node_size=[node_base + (m * node_scale) for m in masas], 
            node_color=masas, cmap=plt.cm.YlOrRd, edgecolors='black')
        
        nx.draw_networkx_edges(G, posicion, alpha=alfa_aristas, arrows=True, arrowsize=tamano_flecha, arrowstyle='-|>', edge_color='gray')
        nx.draw_networkx_labels(G, posicion, font_size=8)
        
        plt.title(titulo)
        plt.axis('off')
        
        base_filename = os.path.join(ruta_imagenes, f"{titulo.replace(' ', '_')}")
        
        for fmt in formatos:
            if fmt == 'pkl':
                with open(f"{base_filename}.pkl", "wb") as f:
                    pickle.dump(fig, f)
            else:
                plt.savefig(f"{base_filename}.{fmt}", format=fmt, bbox_inches='tight')
                
        if mostrar_grafico:
            plt.show()
            
        plt.close(fig)

        if exportar_gephi:
            ruta_gephi = os.path.join(ruta_base, "archivos_gephi")
            os.makedirs(ruta_gephi, exist_ok=True)
            nx.write_gexf(G, os.path.join(ruta_gephi, f"{titulo.replace(' ', '_')}.gexf"))

    @staticmethod
    def exportar_mega_dashboard(diccionario_simulaciones, ruta_base, nombre_archivo="panel_control_total.html"):
        fig_final = go.Figure()
        
        min_m, max_m = _DashboardManager.get_global_mass_range(diccionario_simulaciones)
        fig_final.add_trace(_DashboardManager.create_dummy_colorbar(min_m, max_m))
        
        mapeo_trazas = _DashboardManager.add_traces_to_master(fig_final, diccionario_simulaciones)
        
        botones_capas = _DashboardManager.generate_buttons(diccionario_simulaciones, mapeo_trazas, len(fig_final.data))

        fig_final.update_layout(
            updatemenus=[dict(buttons=botones_capas, direction="down", showactive=True, x=0.05, xanchor="left", y=1.08, yanchor="top", bgcolor="white")],
            annotations=[dict(text="<b>CAPA:</b>", showarrow=False, x=0.05, xref="paper", y=1.12, yref="paper", align="left")],
            title=dict(text="Panel Maestro de Difusión", x=0.5, y=0.95),
            scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), aspectmode='data'),
            margin=dict(l=0, r=50, b=0, t=100),
            showlegend=False
        )

        if len(botones_capas) > 0:
            first_vis = botones_capas[0]['args'][0]['visible']
            for i, visible in enumerate(first_vis):
                fig_final.data[i].visible = visible
        
        fig_final.write_html(os.path.join(ruta_base, nombre_archivo))