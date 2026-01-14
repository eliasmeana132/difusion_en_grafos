import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import os
import plotly.graph_objects as go

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
                a_x.append(x0 + 0.8 * vx); a_y.append(y0 + 0.8 * vy); a_z.append(z0 + 0.8 * vz)
                a_u.append(vx / length); a_v.append(vy / length); a_w.append(vz / length)

        trace_edges = go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, line=dict(width=1, color='#dbdbdb'), hoverinfo='none', mode='lines', name='Aristas')
        trace_arrows = go.Cone(x=a_x, y=a_y, z=a_z, u=a_u, v=a_v, w=a_w, sizeref=0.05, anchor="tail", showscale=False, colorscale=[[0, '#dbdbdb'], [1, '#dbdbdb']], opacity=0.6, name='Dirección')

        masas = [G.nodes[n]['val'] for n in G.nodes()]
        trace_nodes = go.Scatter3d(
            x=[pos_3d[n][0] for n in G.nodes()], y=[pos_3d[n][1] for n in G.nodes()], z=[pos_3d[n][2] for n in G.nodes()],
            mode='markers',
            marker=dict(symbol='circle', size=[2 + (m * 8) for m in masas], color=masas, colorscale='YlOrRd', line=dict(color='black', width=0.5), showscale=True, colorbar=dict(title='Masa', thickness=15)),
            text=[f"Nodo: {n}<br>Masa: {m:.4f}" for n, m in zip(G.nodes(), masas)], hoverinfo='text', name='Nodos'
        )
        fig = go.Figure(data=[trace_edges, trace_arrows, trace_nodes])
        fig.update_layout(title=titulo, scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), aspectmode='data'), margin=dict(l=0, r=0, b=0, t=40), showlegend=False)
        return fig

    @staticmethod
    def renderizar_3d(G, titulo, ruta_base):
        fig = VisualizadorPelado.generar_figura_3d(G, titulo)
        if fig:
            ruta_3d = os.path.join(ruta_base, "renders_3d")
            os.makedirs(ruta_3d, exist_ok=True)
            fig.write_html(os.path.join(ruta_3d, f"{titulo.replace(' ', '_')}.html"))

    @staticmethod
    def exportar_dashboard_interactivo(figuras_lista, titulos_lista, ruta_base, nombre_archivo="dashboard_interactivo.html"):
        VisualizadorPelado.exportar_mega_dashboard({"Resultados": figuras_lista}, ruta_base, nombre_archivo)

    @staticmethod
    def renderizar(G, titulo, ruta_base, exportar_gephi=True, mostrar_grafico=False, k_layout=None, alfa_aristas=0.3, tamano_flecha=15):
        if len(G.nodes()) == 0: return
        ruta_imagenes = os.path.join(ruta_base, "imagenes_grafos")
        os.makedirs(ruta_imagenes, exist_ok=True)
        plt.figure(figsize=(14, 10))
        posicion = nx.spring_layout(G, k=k_layout if k_layout else 0.3, seed=42)
        masas = [G.nodes[n]['val'] for n in G.nodes()]
        nodos = nx.draw_networkx_nodes(G, posicion, node_size=[100 + (m * 300) for m in masas], node_color=masas, cmap=plt.cm.YlOrRd, edgecolors='black')
        nx.draw_networkx_edges(G, posicion, alpha=alfa_aristas, arrows=True, arrowsize=tamano_flecha, arrowstyle='-|>', edge_color='gray')
        nx.draw_networkx_labels(G, posicion, font_size=8)
        if exportar_gephi:
            ruta_gephi = os.path.join(ruta_base, "archivos_gephi"); os.makedirs(ruta_gephi, exist_ok=True)
            nx.write_gexf(G, os.path.join(ruta_gephi, f"{titulo.replace(' ', '_')}.gexf"))
        plt.title(titulo); plt.axis('off'); plt.savefig(os.path.join(ruta_imagenes, f"{titulo.replace(' ', '_')}.png")); plt.close()

    @staticmethod
    def exportar_mega_dashboard(diccionario_simulaciones, ruta_base, nombre_archivo="panel_control_total.html"):
        fig_final = go.Figure()
        mapeo_trazas = []
        trace_counter = 0

        all_masses = []
        for list_figs in diccionario_simulaciones.values():
            for f in list_figs:
                if len(f.data) > 2:
                    all_masses.extend(f.data[2].marker.color)
        
        min_m, max_m = (min(all_masses), max(all_masses)) if all_masses else (0, 1)

        fig_final.add_trace(go.Scatter3d(
            x=[None], y=[None], z=[None],
            mode='markers',
            marker=dict(
                colorscale='YlOrRd',
                cmin=min_m, cmax=max_m,
                showscale=True,
                colorbar=dict(title='Masa', thickness=20, x=1.0, len=0.7, y=0.5)
            ),
            showlegend=False
        ))
        trace_counter += 1

        for sim_nombre, lista_figs in diccionario_simulaciones.items():
            for i, fig in enumerate(lista_figs):
                num_trazas_en_fig = len(fig.data)
                indices_trazas = list(range(trace_counter, trace_counter + num_trazas_en_fig))
                for trace in fig.data:
                    trace.visible = False
                    trace.showlegend = False
                    if hasattr(trace, 'marker') and trace.marker and hasattr(trace.marker, 'showscale'):
                        trace.marker.showscale = False
                    fig_final.add_trace(trace)
                mapeo_trazas.append({"sim": sim_nombre, "capa": i, "indices": indices_trazas})
                trace_counter += num_trazas_en_fig

        botones_capas = []
        
        for sim_nombre in diccionario_simulaciones.keys():
            max_capas = len(diccionario_simulaciones[sim_nombre])
            for c in range(max_capas):
                visibilidad = [False] * len(fig_final.data)
                visibilidad[0] = True
                for m in mapeo_trazas:
                    if m["sim"] == sim_nombre and m["capa"] == c:
                        for idx in m["indices"]: visibilidad[idx] = True
                botones_capas.append(dict(label=f"{sim_nombre} - Capa {c+1}", method="update", args=[{"visible": visibilidad}, {"title": f"Red: {sim_nombre} | Capa {c+1}"}]))

        fig_final.update_layout(
            updatemenus=[
                dict(buttons=botones_capas, direction="down", showactive=True, x=0.05, xanchor="left", y=1.08, yanchor="top", bgcolor="white")
            ],
            annotations=[
                dict(text="<b>CAPA:</b>", showarrow=False, x=0.05, xref="paper", y=1.12, yref="paper", align="left")
            ],
            title=dict(text="Panel Maestro de Difusión", x=0.5, y=0.95),
            scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), aspectmode='data'),
            margin=dict(l=0, r=50, b=0, t=100),
            showlegend=False
        )

        if len(botones_capas) > 0:
            initial_vis = [False] * len(fig_final.data)
            initial_vis[0] = True
            first_button = botones_capas[0]
            first_button_vis = first_button['args'][0]['visible']
            for i, visible in enumerate(first_button_vis):
                fig_final.data[i].visible = visible
        
        fig_final.write_html(os.path.join(ruta_base, nombre_archivo))